"""Backward-compatible re-export of the connection health service.

New code should import from src.shared.services.connection_health_service
"""

from src.shared.services.connection_health_service import ConnectionHealthService

__all__ = ["ConnectionHealthService"]
