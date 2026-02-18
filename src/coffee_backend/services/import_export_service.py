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
from coffee_backend.db.models.enums import BrewStatus
from coffee_backend.schemas.import_export import (
    CSVExportResult,
    CSVImportError,
    CSVImportRequest,
    CSVImportResult,
)
from coffee_backend.schemas.parameter_registry import METHOD_PARAMETER_REGISTRY
from coffee_backend.services.parameter_validation import validate_method_parameters

LEGACY_IMPORT_ALIASES: dict[str, dict[str, str]] = {
    "aeropress": {
        "coffee amount": "coffee_g",
        "grinder setting": "grind_size",
        "temperature": "water_temp",
        "brewing time": "brew_time_sec",
        "anti-static water": "water_g",
    }
}

LEGACY_EXTRA_DATA_KEYS: dict[str, set[str]] = {"aeropress": {"brand", "pressing time"}}


class ImportExportService:
    BATCH_SIZE = 250

    def __init__(self, db: Session):
        self.db = db

    def _hash_brew(
        self, user_id: UUID, brewed_at: datetime, params: dict[str, object], score: object
    ) -> str:
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

    def _parse_param_value(self, value: str) -> object:
        if value.replace(".", "", 1).isdigit():
            if "." in value:
                return float(value)
            return int(value)
        return value

    def _normalise_legacy_param(self, method: str, key: str, value: object) -> object:
        if method == "aeropress" and key == "grind_size" and isinstance(value, int) and value > 15:
            return max(1, min(15, round(value / 4)))
        return value

    def _is_legacy_reviewer_column(self, key: str) -> bool:
        return key.isalpha() and key[:1].isupper()

    def import_csv(self, user_id: UUID, request: CSVImportRequest) -> CSVImportResult:
        data_path = Path(request.data_path)
        if not data_path.exists():
            raise ValidationError("Data file not found", code="data_file_not_found")

        method = request.method or data_path.name.split(".")[0]
        schema = METHOD_PARAMETER_REGISTRY.get(method)
        inserted = 0
        skipped = 0
        processed = 0
        errors: list[CSVImportError] = []
        seen_import_hashes: set[str] = set()
        pending_inserts = 0

        with data_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row_index, row in enumerate(reader, start=2):
                processed += 1
                try:
                    brewed_at = datetime.fromisoformat(
                        row.get("date", datetime.now(timezone.utc).isoformat())
                    )
                    score_value = row.get("score")
                    score = float(score_value) if score_value not in (None, "") else None
                    failed = row.get("failed", "false").lower() == "true"
                    status = BrewStatus.FAILED if failed else BrewStatus.OK
                    comments = row.get("comments")
                    known = {"date", "score", "failed", "comments", "method"}
                    aliases = LEGACY_IMPORT_ALIASES.get(method, {})
                    extra_keys = LEGACY_EXTRA_DATA_KEYS.get(method, set())
                    params: dict[str, object] = {}
                    extra_data: dict[str, object] = {}

                    for raw_key, raw_value in row.items():
                        if raw_key in known or raw_value in (None, ""):
                            continue

                        parsed_value = self._parse_param_value(raw_value)
                        key = aliases.get(raw_key, raw_key)

                        if schema is not None and key in schema:
                            params[key] = self._normalise_legacy_param(method, key, parsed_value)
                            continue

                        if raw_key in extra_keys or self._is_legacy_reviewer_column(raw_key):
                            extra_data[raw_key] = parsed_value
                            continue

                        raise ValidationError(
                            "Unknown parameter keys",
                            code="unknown_parameter_keys",
                            fields={raw_key: "unknown parameter"},
                        )

                    validate_method_parameters(method, params)

                    import_hash = self._hash_brew(user_id, brewed_at, params, score)
                    if import_hash in seen_import_hashes:
                        skipped += 1
                        continue

                    existing = self.db.scalar(
                        select(Brew.id).where(Brew.import_hash == import_hash)
                    )
                    if existing:
                        skipped += 1
                        seen_import_hashes.add(import_hash)
                        continue

                    seen_import_hashes.add(import_hash)

                    brew = Brew(
                        user_id=user_id,
                        method=method,
                        parameters=params,
                        extra_data=extra_data or None,
                        brewed_at=brewed_at,
                        score=score,
                        status=status,
                        comments=comments,
                        import_hash=import_hash,
                    )
                    self.db.add(brew)
                    inserted += 1
                    pending_inserts += 1

                    if pending_inserts >= self.BATCH_SIZE:
                        self.db.flush()
                        self.db.commit()
                        pending_inserts = 0
                except ValidationError as exc:
                    skipped += 1
                    errors.append(
                        CSVImportError(
                            row=row_index,
                            detail=exc.detail,
                            code=exc.code,
                            fields=exc.fields,
                        )
                    )

        if pending_inserts:
            self.db.flush()
        self.db.commit()
        return CSVImportResult(
            processed=processed,
            inserted=inserted,
            imported=inserted,
            skipped=skipped,
            error_count=len(errors),
            errors=errors,
        )

    def export_csv(self, user_id: UUID, out_dir: str) -> CSVExportResult:
        output = Path(out_dir)
        output.mkdir(parents=True, exist_ok=True)
        brews = list(
            self.db.scalars(select(Brew).where(Brew.user_id == user_id).order_by(Brew.brewed_at))
        )
        path = output / "brews.export.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            fieldnames = [
                "id",
                "method",
                "brewed_at",
                "score",
                "status",
                "comments",
                "parameters",
                "extra_data",
            ]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for brew in brews:
                writer.writerow(
                    {
                        "id": brew.id,
                        "method": brew.method,
                        "brewed_at": brew.brewed_at.isoformat(),
                        "score": brew.score,
                        "status": (
                            brew.status.value if hasattr(brew.status, "value") else brew.status
                        ),
                        "comments": brew.comments,
                        "parameters": json.dumps(brew.parameters),
                        "extra_data": json.dumps(brew.extra_data),
                    }
                )
        return CSVExportResult(output_files=[str(path)])
