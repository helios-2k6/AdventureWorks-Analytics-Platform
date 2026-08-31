class BaseConnector:
    """Shared base class for all database connectors."""

    def __init__(self):
        self.connection = None

    def connect(self):
        raise NotImplementedError("Connector subclasses must implement connect().")

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
