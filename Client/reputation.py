"""
Manages node reputation scores based on performance and reliability.
"""
import json


class ReputationManager:
    """Handles loading, updating, and saving node reputation scores."""

    def __init__(self, filepath: str = 'reputation.json'):
        self.filepath = filepath
        self.scores = self._load()

    def _load(self) -> dict:
        """Load reputation scores from file."""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self):
        """Save current reputation scores to file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.scores, f, indent=2)

    def update_score(self, node_id: str, change: float):
        """Update a node's score and save."""
        current_score = self.scores.get(node_id, 1.0)
        self.scores[node_id] = max(0, current_score + change)
        self._save()

    def get_score(self, node_id: str) -> float:
        """Get a node's current score."""
        return self.scores.get(node_id, 1.0)
