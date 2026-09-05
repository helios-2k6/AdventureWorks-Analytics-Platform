from __future__ import annotations

from collections.abc import Mapping


REQUIRED_BRONZE_TARGETS = (
    "bronze.sales_order_header",
    "bronze.sales_order_detail",
    "bronze.customer",
    "bronze.sales_territory",
    "bronze.sales_person",
    "bronze.product",
    "bronze.person",
)


class BronzeSnapshotGate:
    """Validate one complete, published Bronze snapshot before Silver runs."""

    allowed_statuses = {"SUCCESS", "SUCCESS_WITH_REJECTIONS"}

    def __init__(self, required_targets: tuple[str, ...] = REQUIRED_BRONZE_TARGETS):
        self.required_targets = tuple(required_targets)

    def validate(
        self,
        bronze_result: Mapping[str, Mapping[str, object]],
        snapshot_id: str,
    ) -> dict[str, object]:
        failures: list[str] = []
        identities: set[str] = set()
        for target in self.required_targets:
            short_target = target.removeprefix("bronze.")
            result = bronze_result.get(target) or bronze_result.get(short_target)
            if result is None:
                result = next(
                    (
                        candidate
                        for candidate in bronze_result.values()
                        if isinstance(candidate, Mapping)
                        and candidate.get("target_table") in {target, short_target}
                    ),
                    None,
                )
            if not isinstance(result, Mapping):
                failures.append(f"missing Bronze result: {target}")
                continue
            if result.get("status") not in self.allowed_statuses:
                failures.append(
                    f"Bronze table is not successful: {target} "
                    f"status={result.get('status')}"
                )
            if result.get("published") is not True:
                failures.append(f"Bronze table is not published: {target}")
            if not result.get("run_id") or not result.get("load_id"):
                failures.append(
                    f"Bronze source identity is missing: {target} requires run_id/load_id"
                )
            result_snapshot = result.get("snapshot_id")
            if result_snapshot is None:
                failures.append(f"Bronze snapshot identity is missing: {target}")
            else:
                identities.add(str(result_snapshot))

        if identities != {snapshot_id}:
            failures.append(
                f"Bronze snapshot identity mismatch: expected={snapshot_id}, "
                f"found={sorted(identities)}"
            )

        return {
            "status": "SUCCESS" if not failures else "FAILED",
            "snapshot_id": snapshot_id,
            "required_targets": list(self.required_targets),
            "failures": failures,
            "table_count": len(self.required_targets),
        }
