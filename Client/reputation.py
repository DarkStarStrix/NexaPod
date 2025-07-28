"""
Module for managing user reputation.
"""

class ReputationManager:
    """Handles reputation value and updates."""
    def __init__(self, initial_value: int = 0):
        self.reputation = initial_value

    def update_reputation(self, change: int) -> int:
        """Update reputation by change and return new value."""
        self.reputation += change
        return self.reputation


def main():
    """Demo script for ReputationManager."""
    manager = ReputationManager()
    print("Initial reputation:", manager.reputation)
    changes = [10, -20, 15, -5, 25]
    for change in changes:
        new_reputation = manager.update_reputation(change)
        print(f"Applied change {change}: Reputation is now {new_reputation}")


if __name__ == "__main__":
    main()
