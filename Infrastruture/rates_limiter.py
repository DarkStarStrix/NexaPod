import asyncio
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Union, Callable

import redis

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests: int  # Number of requests allowed
    window: int    # Time window in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_allowance: Optional[int] = None  # Extra requests for burst traffic


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after


class TokenBucket:
    """Token bucket implementation for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens from the bucket."""
        with self.lock:
            now = time.time()
            # Add tokens based on time elapsed
            time_passed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def time_until_available(self, tokens: int = 1) -> float:
        """Calculate time until enough tokens are available."""
        with self.lock:
            if self.tokens >= tokens:
                return 0
            needed_tokens = tokens - self.tokens
            return needed_tokens / self.refill_rate


class SlidingWindowCounter:
    """Sliding window counter for rate limiting."""

    def __init__(self, window_size: int):
        self.window_size = window_size
        self.requests = deque()
        self.lock = threading.Lock()

    def add_request(self) -> bool:
        """Add a request and return if within rate limit."""
        now = time.time()
        with self.lock:
            # Remove old requests outside the window
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()

            self.requests.append(now)
            return True

    def get_count(self) -> int:
        """Get current request count in the window."""
        now = time.time()
        with self.lock:
            # Remove old requests
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()
            return len(self.requests)

    def time_until_reset(self) -> float:
        """Time until the oldest request expires."""
        if not self.requests:
            return 0
        return max(0, self.requests[0] + self.window_size - time.time())


class RedisRateLimiter:
    """Redis-based distributed rate limiter."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def check_rate_limit(self, key: str, limit: RateLimit) -> tuple[bool, int]:
        """Check rate limit using Redis."""
        if limit.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._sliding_window_redis(key, limit)
        elif limit.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._fixed_window_redis(key, limit)
        else:
            raise ValueError(f"Strategy {limit.strategy} not supported for Redis")

    def _sliding_window_redis(self, key: str, limit: RateLimit) -> tuple[bool, int]:
        """Sliding window implementation using Redis."""
        now = time.time()
        window_start = now - limit.window

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, limit.window)
        results = pipe.execute()

        current_count = results[1]
        allowed = current_count < limit.requests
        retry_after = 0 if allowed else limit.window

        return allowed, retry_after

    def _fixed_window_redis(self, key: str, limit: RateLimit) -> tuple[bool, int]:
        """Fixed window implementation using Redis."""
        now = int(time.time())
        window = now // limit.window * limit.window
        window_key = f"{key}:{window}"

        pipe = self.redis.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, limit.window)
        results = pipe.execute()

        current_count = results[0]
        allowed = current_count <= limit.requests
        retry_after = 0 if allowed else limit.window - (now % limit.window)

        return allowed, retry_after


class InMemoryRateLimiter:
    """In-memory rate limiter for single-instance applications."""

    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.counters: Dict[str, SlidingWindowCounter] = {}
        self.fixed_windows: Dict[str, Dict[int, int]] = defaultdict(dict)
        self.lock = threading.Lock()

    def check_rate_limit(self, key: str, limit: RateLimit) -> tuple[bool, int]:
        """Check rate limit for a given key."""
        if limit.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._check_token_bucket(key, limit)
        elif limit.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._check_sliding_window(key, limit)
        elif limit.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._check_fixed_window(key, limit)
        else:
            raise ValueError(f"Unsupported strategy: {limit.strategy}")

    def _check_token_bucket(self, key: str, limit: RateLimit) -> tuple[bool, int]:
        """Token bucket rate limiting."""
        if key not in self.buckets:
            with self.lock:
                if key not in self.buckets:
                    refill_rate = limit.requests / limit.window
                    self.buckets[key] = TokenBucket(limit.requests, refill_rate)

        bucket = self.buckets[key]
        if bucket.consume():
            return True, 0
        else:
            retry_after = int(bucket.time_until_available())
            return False, retry_after

    def _check_sliding_window(self, key: str, limit: RateLimit) -> tuple[bool, int]:
        """Sliding window rate limiting."""
        if key not in self.counters:
            with self.lock:
                if key not in self.counters:
                    self.counters[key] = SlidingWindowCounter(limit.window)

        counter = self.counters[key]
        counter.add_request()

        if counter.get_count() <= limit.requests:
            return True, 0
        else:
            retry_after = int(counter.time_until_reset())
            return False, retry_after

    def _check_fixed_window(self, key: str, limit: RateLimit) -> tuple[bool, int]:
        """Fixed window rate limiting."""
        now = int(time.time())
        window = now // limit.window * limit.window

        with self.lock:
            if window not in self.fixed_windows[key]:
                self.fixed_windows[key][window] = 0

            # Clean old windows
            old_windows = [w for w in self.fixed_windows[key] if w < window - limit.window]
            for old_window in old_windows:
                del self.fixed_windows[key][old_window]

            current_count = self.fixed_windows[key][window]
            if current_count < limit.requests:
                self.fixed_windows[key][window] += 1
                return True, 0
            else:
                retry_after = limit.window - (now % limit.window)
                return False, retry_after


class RateLimiter:
    """Main rate limiter class with multiple backend support."""

    def __init__(self,
                 backend: Union[InMemoryRateLimiter, RedisRateLimiter] = None,
                 default_limits: Optional[Dict[str, RateLimit]] = None):
        self.backend = backend or InMemoryRateLimiter()
        self.default_limits = default_limits or {}
        self.custom_limits: Dict[str, RateLimit] = {}

    def add_limit(self, name: str, limit: RateLimit):
        """Add a custom rate limit."""
        self.custom_limits[name] = limit

    def check_limit(self,
                   identifier: str,
                   limit_name: str = "default",
                   custom_limit: Optional[RateLimit] = None) -> tuple[bool, int]:
        """Check if request is within rate limit."""
        # Determine which limit to use
        if custom_limit:
            limit = custom_limit
        elif limit_name in self.custom_limits:
            limit = self.custom_limits[limit_name]
        elif limit_name in self.default_limits:
            limit = self.default_limits[limit_name]
        else:
            raise ValueError(f"No rate limit defined for: {limit_name}")

        key = f"{limit_name}:{identifier}"
        return self.backend.check_rate_limit(key, limit)

    def enforce_limit(self,
                     identifier: str,
                     limit_name: str = "default",
                     custom_limit: Optional[RateLimit] = None):
        """Enforce rate limit, raising exception if exceeded."""
        allowed, retry_after = self.check_limit(identifier, limit_name, custom_limit)
        if not allowed:
            raise RateLimitExceeded(
                f"Rate limit exceeded for {limit_name}",
                retry_after
            )


# Decorator for rate limiting functions
def rate_limit(limiter: RateLimiter,
               limit_name: str = "default",
               identifier_func: Callable = None):
    """Decorator to apply rate limiting to functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Determine identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = "global"

            # Check rate limit
            limiter.enforce_limit(identifier, limit_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Async version for asyncio applications
class AsyncRateLimiter:
    """Async rate limiter using asyncio locks."""

    def __init__(self, sync_limiter: RateLimiter):
        self.sync_limiter = sync_limiter
        self._lock = asyncio.Lock()

    async def check_limit(self,
                         identifier: str,
                         limit_name: str = "default",
                         custom_limit: Optional[RateLimit] = None) -> tuple[bool, int]:
        """Async check rate limit."""
        async with self._lock:
            return self.sync_limiter.check_limit(identifier, limit_name, custom_limit)

    async def enforce_limit(self,
                           identifier: str,
                           limit_name: str = "default",
                           custom_limit: Optional[RateLimit] = None):
        """Async enforce rate limit."""
        async with self._lock:
            self.sync_limiter.enforce_limit(identifier, limit_name, custom_limit)


# Example usage and configuration
def create_nexapod_rate_limiter() -> RateLimiter:
    """Create rate limiter with NEXAPod-specific limits."""

    # Define rate limits for different endpoints
    limits = {
        "api_general": RateLimit(100, 60),  # 100 requests per minute
        "api_compute": RateLimit(10, 60),   # 10 compute requests per minute
        "api_auth": RateLimit(5, 300),      # 5 auth attempts per 5 minutes
        "dashboard": RateLimit(1000, 3600), # 1000 dashboard requests per hour
        "job_submission": RateLimit(20, 3600), # 20 jobs per hour
        "node_registration": RateLimit(5, 86400), # 5 registrations per day
    }

    # Use Redis for distributed setup, or in-memory for single instance
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        backend = RedisRateLimiter(redis_client)
        logger.info("Using Redis backend for rate limiting")
    except:
        backend = InMemoryRateLimiter()
        logger.info("Using in-memory backend for rate limiting")

    return RateLimiter(backend, limits)


# Flask/FastAPI integration examples
def get_client_ip(request) -> str:
    """Extract client IP from request."""
    return request.environ.get('HTTP_X_FORWARDED_FOR',
                              request.environ.get('REMOTE_ADDR', 'unknown'))


# Example Flask middleware
def flask_rate_limit_middleware(app, limiter: RateLimiter):
    """Flask middleware for rate limiting."""

    @app.before_request
    def check_rate_limit():
        from flask import request, jsonify

        # Skip rate limiting for certain paths
        if request.path.startswith('/static/'):
            return

        client_ip = get_client_ip(request)
        endpoint = request.endpoint or 'unknown'

        # Map endpoints to rate limit names
        limit_map = {
            'api.compute': 'api_compute',
            'api.auth': 'api_auth',
            'dashboard': 'dashboard',
        }

        limit_name = limit_map.get(endpoint, 'api_general')

        try:
            limiter.enforce_limit(client_ip, limit_name)
        except RateLimitExceeded as e:
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': e.retry_after
            }), 429