"""
Module defining descriptors for infrastructure components.
"""
from dataclasses import dataclass


@dataclass
class RateLimitDescriptor:
    """Descriptor for rate limiter configuration."""
    max_calls: int
    period_seconds: float


__all__ = ["RateLimitDescriptor"]
