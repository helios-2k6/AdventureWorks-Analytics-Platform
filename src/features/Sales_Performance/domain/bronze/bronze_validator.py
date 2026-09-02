class BronzeValidator:
    """Validate count parity and Bronze quality checks for sales extraction."""

    def validate(self, source_count: int, target_count: int, source_table: str, bronze_table: str) -> bool:
        if source_count == target_count:
            return True
        raise ValueError(
            f"Validation failed for {source_table} -> {bronze_table}: "
            f"source={source_count}, target={target_count}"
        )

    def validate_table(
        self,
        source_count: int,
        target_count: int,
        source_table: str,
        bronze_table: str,
        lineage_columns=None,
        critical_columns=None,
        null_counts=None,
    ) -> dict:
        """Run Bronze validation checks and return a report dictionary."""
        required_lineage = lineage_columns or ["_source_system", "_source_table", "_load_date", "_record_hash"]
        required_critical = critical_columns or {}
        null_summary = null_counts or {}

        issues = []
        count_match = source_count == target_count
        if not count_match:
            issues.append(
                f"Row count mismatch for {source_table} -> {bronze_table}: "
                f"source={source_count}, target={target_count}"
            )

        lineage_columns_ok = all(column in required_lineage for column in ["_source_system", "_source_table", "_load_date", "_record_hash"])
        if not lineage_columns_ok:
            issues.append(f"Missing lineage columns in {bronze_table}: expected metadata fields")

        critical_columns_ok = True
        for column, allowed_nulls in required_critical.items():
            null_count = null_summary.get(column, 0)
            if null_count > allowed_nulls:
                critical_columns_ok = False
                issues.append(
                    f"Critical column {column} exceeds allowed NULL tolerance in {bronze_table}: "
                    f"null_count={null_count}, allowed={allowed_nulls}"
                )

        result = {
            "source_table": source_table,
            "bronze_table": bronze_table,
            "source_count": source_count,
            "target_count": target_count,
            "count_match": count_match,
            "lineage_columns_ok": lineage_columns_ok,
            "critical_columns_ok": critical_columns_ok,
            "validation_passed": count_match and lineage_columns_ok and critical_columns_ok,
            "issues": issues,
        }
        return result
