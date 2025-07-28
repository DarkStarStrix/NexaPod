"""
Node model representing a cluster participant.
"""

import platform
from .tier import Tier


class Node:
    """Represents a compute node with profiling data."""

    def __init__(self, id: str, tier: Tier):
        self.id = id
        self.tier = tier
        self.profile = self._profile_node()

    @staticmethod
    def _profile_node() -> dict:
        """Collect and return basic system profile."""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "processor": platform.processor(),
        }
