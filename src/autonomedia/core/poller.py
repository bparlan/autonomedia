class StatusPoller:
    def should_process(self, platform: dict) -> bool:
        return not platform.get("is_paused", False)
