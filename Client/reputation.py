class ReputationManager:
    def __init__(self):
        # ...existing code...
        self.reputation = 0.0

    def update_reputation(self, change: float) -> float:
        """Update reputation by applying the change and clamping the result between 0 and 100."""
        # ...existing code...
        self.reputation += change
        self.reputation = max(0.0, min(self.reputation, 100.0))
        return self.reputation
