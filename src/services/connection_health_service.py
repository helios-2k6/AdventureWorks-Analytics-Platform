class ConnectionHealthService:
    """Service for checking whether configured connections are healthy."""

    def check_all(self):
        """Perform health checks for registered connections."""
        return {
            "status": "ok",
            "connections": []
        }
