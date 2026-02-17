import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from coffee_backend.core.exceptions import ValidationError
from coffee_backend.db.models.brew import Brew
from coffee_backend.schemas.import_export import CSVExportResult, CSVImportRequest, CSVImportResult
from coffee_backend.services.parameter_validation import validate_method_parameters


class ImportExportService:
    def __init__(self, db: Session):
        self.db = db

    def _hash_brew(self, user_id: UUID, brewed_at: datetime, params: dict[str, object], score: object) -> str:
        payload = json.dumps(
            {
                "user_id": str(user_id),
                "brewed_at": brewed_at.isoformat(),
                "parameters": params,
                "score": score,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def import_csv(self, user_id: UUID, request: CSVImportRequest) -> CSVImportResult:
        data_path = Path(request.data_path)
        if not data_path.exists():
            raise ValidationError("Data file not found")
        method = request.method or data_path.name.split(".")[0]
        imported = 0
        skipped = 0
        with data_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                brewed_at = datetime.fromisoformat(row.get("date", datetime.now(timezone.utc).isoformat()))
                score_value = row.get("score")
                score = float(score_value) if score_value not in (None, "") else None
                failed = row.get("failed", "false").lower() == "true"
                comments = row.get("comments")
                known = {"date", "score", "failed", "comments", "method"}
                params: dict[str, object] = {}
                extra: dict[str, object] = {}
                for key, value in row.items():
                    if key in known:
                        continue
                    if value is None or value == "":
                        continue
                    if value.replace(".", "", 1).isdigit():
                        if "." in value:
                            params[key] = float(value)
                        else:
                            params[key] = int(value)
                    else:
                        params[key] = value
                try:
                    validate_method_parameters(method, params)
                except ValidationError:
                    extra.update(params)
                    params = {}
                import_hash = self._hash_brew(user_id, brewed_at, params, score)
                existing = self.db.scalar(select(Brew).where(Brew.import_hash == import_hash))
                if existing:
                    skipped += 1
                    continue
                brew = Brew(
                    user_id=user_id,
                    method=method,
                    parameters=params,
                    extra_data=extra or None,
                    brewed_at=brewed_at,
                    score=score,
                    failed=failed,
                    comments=comments,
                    import_hash=import_hash,
                )
                self.db.add(brew)
                imported += 1
        self.db.commit()
        return CSVImportResult(imported=imported, skipped=skipped)

    def export_csv(self, user_id: UUID, out_dir: str) -> CSVExportResult:
        output = Path(out_dir)
        output.mkdir(parents=True, exist_ok=True)
        brews = list(self.db.scalars(select(Brew).where(Brew.user_id == user_id).order_by(Brew.brewed_at)))
        path = output / "brews.export.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            fieldnames = ["id", "method", "brewed_at", "score", "failed", "comments", "parameters", "extra_data"]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for brew in brews:
                writer.writerow(
                    {
                        "id": brew.id,
                        "method": brew.method,
                        "brewed_at": brew.brewed_at.isoformat(),
                        "score": brew.score,
                        "failed": brew.failed,
                        "comments": brew.comments,
                        "parameters": json.dumps(brew.parameters),
                        "extra_data": json.dumps(brew.extra_data),
                    }
                )
        return CSVExportResult(output_files=[str(path)])
