from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.persistence import Brew, User
from app.services.auth_service import AuthService

BASE_COLUMNS = {
    'date',
    'brand',
    'coffee amount',
    'grinder setting',
    'anti-static water',
    'temperature',
    'brewing time',
    'pressing time',
    'blooming time',
    'pour amount',
    'pour interval',
    'comments',
    'failed',
}


def normalize_name(value: str) -> str:
    slug = ''.join(ch.lower() if ch.isalnum() else '-' for ch in value).strip('-')
    slug = '-'.join(filter(None, slug.split('-')))
    return slug or 'taster'


def parse_date(value: object) -> datetime:
    if pd.isna(value):
        return datetime.utcnow()
    return pd.to_datetime(value).to_pydatetime()


def to_int(value: object, default: int) -> int:
    if pd.isna(value):
        return default
    return int(round(float(value)))


def to_float(value: object, default: float) -> float:
    if pd.isna(value):
        return default
    return float(value)


def brew_time_from_row(row: pd.Series) -> int:
    if 'brewing time' in row and not pd.isna(row['brewing time']):
        return to_int(row['brewing time'], 150)

    bloom = to_int(row.get('blooming time', 90), 90)
    pour_interval = to_int(row.get('pour interval', 15), 15)
    pour_amount = to_int(row.get('pour amount', 10), 10)
    return max(60, bloom + (pour_interval * max(1, pour_amount // 5)))


def press_time_from_row(row: pd.Series) -> int:
    if 'pressing time' in row and not pd.isna(row['pressing time']):
        return to_int(row['pressing time'], 30)
    return 30


def get_or_create_user(db, name: str) -> User:
    email = f"{normalize_name(name)}@import.local"
    user = db.scalar(select(User).where(User.email == email))
    if user:
        return user

    user = User(email=email, hashed_password=AuthService.hash_password('imported-password'))
    db.add(user)
    db.flush()
    return user


def import_dataset(db, csv_path: Path, method: str) -> int:
    frame = pd.read_csv(csv_path)
    scorer_columns = [c for c in frame.columns if c not in BASE_COLUMNS]
    imported = 0

    for _, row in frame.iterrows():
        if not pd.isna(row.get('failed')):
            continue

        created_at = parse_date(row.get('date'))
        coffee_amount = to_float(row.get('coffee amount'), 18.0)
        grinder_setting = to_int(row.get('grinder setting'), 12)
        temperature = to_int(row.get('temperature'), 90)
        anti_static_water = to_int(row.get('anti-static water'), 0)
        brew_time = brew_time_from_row(row)
        press_time = press_time_from_row(row)

        for scorer in scorer_columns:
            score = row.get(scorer)
            if pd.isna(score):
                continue

            user = get_or_create_user(db, scorer)
            brew = Brew(
                user_id=user.id,
                coffee_amount=coffee_amount,
                grinder_setting_clicks=grinder_setting,
                temperature_c=temperature,
                brew_time_seconds=brew_time,
                press_time_seconds=press_time,
                anti_static_water_microliter=anti_static_water,
                method=method,
                score=to_float(score, 0.0),
                created_at=created_at,
            )
            db.add(brew)
            imported += 1

    return imported


def main() -> None:
    parser = argparse.ArgumentParser(description='Populate coffee.db with records from CSV files.')
    parser.add_argument('--data-dir', default='backend/data', help='Directory containing *.data.csv files.')
    parser.add_argument('--reset', action='store_true', help='Delete existing users/brews before importing.')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    csv_files = sorted(data_dir.glob('*.data.csv'))
    if not csv_files:
        raise SystemExit(f'No CSV files found in: {data_dir}')

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if args.reset:
            db.query(Brew).delete()
            db.query(User).delete()
            db.commit()

        total = 0
        for path in csv_files:
            method = path.stem.replace('.data', '')
            count = import_dataset(db, path, method)
            total += count
            print(f'Imported {count} brews from {path.name} as method={method}')

        db.commit()

        user_count = db.query(User).count()
        brew_count = db.query(Brew).count()
        print(f'Done. Users: {user_count}, Brews: {brew_count}, Imported this run: {total}')


if __name__ == '__main__':
    main()
