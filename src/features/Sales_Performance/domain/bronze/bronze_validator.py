class BronzeValidator:
    """Validate count parity between source and Bronze tables."""

    def validate(self, source_count: int, target_count: int, source_table: str, bronze_table: str) -> bool:
        if source_count == target_count:
            return True
        raise ValueError(
            f"Validation failed for {source_table} -> {bronze_table}: "
            f"source={source_count}, target={target_count}"
        )
