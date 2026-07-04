class ErrorResolver:
    def classify(self, exception: Exception) -> str:
        # Simple classification logic
        # Extend as needed
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return "transient"
        return "fatal"
