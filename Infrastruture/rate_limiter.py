"""
Rate limiter implementing a token-bucket algorithm.
"""
import threading
import time
from .Descriptor import RateLimitDescriptor


class RateLimiter:
    """Limits calls to a resource based on a RateLimitDescriptor."""
    def __init__(self, descriptor: RateLimitDescriptor):
        self.max_calls = descriptor.max_calls
        self.period = descriptor.period_seconds
        self._lock = threading.Lock()
        self._timestamps = []

    def acquire(self):
        """Block until a new call is allowed based on rate descriptor."""
        while True:
            with self._lock:
                now = time.time()
                cutoff = now - self.period
                self._timestamps = [ts for ts in self._timestamps
                                   if ts > cutoff]
                if len(self._timestamps) < self.max_calls:
                    self._timestamps.append(now)
                    return
                delay = self.period - (now - self._timestamps[0])
            time.sleep(delay)


def rate_limited(descriptor: RateLimitDescriptor):
    """Decorator to apply rate limiting based on a descriptor."""
    limiter = RateLimiter(descriptor)

    def decorator(func):
        def wrapper(*args, **kwargs):
            limiter.acquire()
            return func(*args, **kwargs)
        return wrapper
    return decorator
