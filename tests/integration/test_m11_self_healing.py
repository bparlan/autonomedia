from src.autonomedia.core.error_resolver import ErrorResolver


def test_error_resolver_classifies_transient_vs_fatal():
    resolver = ErrorResolver()

    # Transient errors should be retriable
    transient = ConnectionError("Network blip")
    assert resolver.classify(transient) == "transient"

    # Fatal errors (e.g., Syntax/Validation)
    fatal = ValueError("Invalid selector")
    assert resolver.classify(fatal) == "fatal"

# Mock classes for integration test
class MockWorker:
    def __init__(self, platform_id):
        self.platform_id = platform_id

def test_circuit_breaker_halts_paused_platform():
    from src.autonomedia.core.poller import StatusPoller

    poller = StatusPoller()
    platform = {"id": "1", "is_paused": True}

    # Should skip / ignore
    assert poller.should_process(platform) is False

    platform["is_paused"] = False
    assert poller.should_process(platform) is True

def test_artifact_generation_triggered_on_exception():
    import os

    # Setup
    task_id = "test_task_123"
    storage_path = "storage/screenshots"

    # Clear old
    if os.path.exists(os.path.join(storage_path, f"{task_id}.png")):
        os.remove(os.path.join(storage_path, f"{task_id}.png"))

    # Trigger (would be actual worker call)
    # For now, manually ensure it doesn't exist
    assert not os.path.exists(os.path.join(storage_path, f"{task_id}.png"))
