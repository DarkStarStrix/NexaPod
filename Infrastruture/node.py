from tier import Tier
import platform

class Node:
    def __init__(self, id, tier: Tier):
        self.id = id
        self.tier = tier
        self.profile = self._profile_node()

    def _profile_node(self):
        # Perform basic profiling (this can be expanded)
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "processor": platform.processor()
        }
