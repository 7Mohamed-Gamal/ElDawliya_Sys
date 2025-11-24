"""
Custom throttling classes for API rate limiting
فئات التحكم في معدل الطلبات المخصصة لـ API
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, BaseThrottle
from django.core.cache import cache
from django.utils import timezone
import time


class APIKeyRateThrottle(BaseThrottle):
    """
    Throttling based on API key with different rates for different key types
    التحكم في المعدل بناءً على مفتاح API مع معدلات مختلفة لأنواع مفاتيح مختلفة
    """
    scope = 'api_key'

    def __init__(self):
        """__init__ function"""
        super().__init__()
        self.rates = {
            'basic': '1000/hour',      # Basic API keys
            'premium': '5000/hour',    # Premium API keys
            'enterprise': '10000/hour' # Enterprise API keys
        }

    def allow_request(self, request, view):
        """
        Check if the request should be allowed based on API key rate limits
        """
        # Get API key from request
        api_key = getattr(request, 'api_key', None)
        if not api_key:
            return True  # No API key, let other throttles handle it

        # Determine rate based on API key type
        key_type = getattr(api_key, 'key_type', 'basic')
        rate = self.rates.get(key_type, self.rates['basic'])

        # Parse rate (e.g., "1000/hour" -> 1000 requests per hour)
        num_requests, period = self.parse_rate(rate)
        if num_requests is None:
            return True

        # Create cache key
        cache_key = f"throttle_api_key_{api_key.key}"

        # Get current request count
        now = timezone.now()
        current_requests = cache.get(cache_key, [])

        # Remove old requests outside the time window
        cutoff_time = now - timezone.timedelta(seconds=period)
        current_requests = [req_time for req_time in current_requests if req_time > cutoff_time]

        # Check if limit exceeded
        if len(current_requests) >= num_requests:
            return False

        # Add current request
        current_requests.append(now)
        cache.set(cache_key, current_requests, period)

        return True

    def parse_rate(self, rate):
        """
        Parse rate string like "1000/hour" into (1000, 3600)
        """
        if rate is None:
            return None, None

        num, period = rate.split('/')
        num_requests = int(num)

        duration = {
            'second': 1,
            'minute': 60,
            'hour': 3600,
            'day': 86400
        }.get(period, 3600)

        return num_requests, duration

    def wait(self):
        """
        Return the recommended next request time in seconds
        """
        return 60  # Default wait time


class PremiumUserRateThrottle(UserRateThrottle):
    """
    Higher rate limits for premium users
    حدود معدل أعلى للمستخدمين المميزين
    """
    scope = 'premium'

    def allow_request(self, request, view):
        """
        Check if user is premium and apply appropriate rate
        """
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if getattr(request.user.profile, 'is_premium', False):
                return super().allow_request(request, view)

        # Fall back to regular user throttling
        regular_throttle = UserRateThrottle()
        return regular_throttle.allow_request(request, view)


class BurstRateThrottle(BaseThrottle):
    """
    Allow burst requests but limit sustained rate
    السماح بطلبات متفجرة ولكن تحديد المعدل المستدام
    """
    scope = 'burst'

    def __init__(self):
        """__init__ function"""
        super().__init__()
        self.burst_rate = 10  # 10 requests per minute
        self.sustained_rate = 100  # 100 requests per hour

    def allow_request(self, request, view):
        """
        Check both burst and sustained rates
        """
        if not request.user.is_authenticated:
            return True

        user_id = request.user.id
        now = time.time()

        # Check burst rate (last minute)
        burst_key = f"throttle_burst_{user_id}"
        burst_requests = cache.get(burst_key, [])
        burst_requests = [req_time for req_time in burst_requests if now - req_time < 60]

        if len(burst_requests) >= self.burst_rate:
            return False

        # Check sustained rate (last hour)
        sustained_key = f"throttle_sustained_{user_id}"
        sustained_requests = cache.get(sustained_key, [])
        sustained_requests = [req_time for req_time in sustained_requests if now - req_time < 3600]

        if len(sustained_requests) >= self.sustained_rate:
            return False

        # Update counters
        burst_requests.append(now)
        sustained_requests.append(now)

        cache.set(burst_key, burst_requests, 60)
        cache.set(sustained_key, sustained_requests, 3600)

        return True


class EndpointSpecificThrottle(BaseThrottle):
    """
    Different rate limits for different endpoints
    حدود معدل مختلفة لنقاط نهاية مختلفة
    """

    def __init__(self):
        """__init__ function"""
        super().__init__()
        self.endpoint_rates = {
            '/api/v1/ai/': '50/hour',        # AI endpoints are more expensive
            '/api/v1/reports/': '200/hour',   # Reports can be resource intensive
            '/api/v1/export/': '20/hour',     # Export operations are limited
            '/api/v1/import/': '10/hour',     # Import operations are very limited
        }

    def allow_request(self, request, view):
        """
        Apply rate limit based on endpoint
        """
        if not request.user.is_authenticated:
            return True

        # Find matching endpoint
        endpoint_rate = None
        for endpoint, rate in self.endpoint_rates.items():
            if request.path.startswith(endpoint):
                endpoint_rate = rate
                break

        if not endpoint_rate:
            return True  # No specific limit for this endpoint

        # Parse rate
        num_requests, period = self.parse_rate(endpoint_rate)
        if num_requests is None:
            return True

        # Create cache key
        cache_key = f"throttle_endpoint_{request.user.id}_{request.path}"

        # Check rate limit
        now = time.time()
        requests = cache.get(cache_key, [])
        requests = [req_time for req_time in requests if now - req_time < period]

        if len(requests) >= num_requests:
            return False

        requests.append(now)
        cache.set(cache_key, requests, period)

        return True

    def parse_rate(self, rate):
        """Parse rate string"""
        if rate is None:
            return None, None

        num, period = rate.split('/')
        num_requests = int(num)

        duration = {
            'second': 1,
            'minute': 60,
            'hour': 3600,
            'day': 86400
        }.get(period, 3600)

        return num_requests, duration


class DynamicRateThrottle(BaseThrottle):
    """
    Dynamic rate limiting based on system load and user behavior
    تحديد المعدل الديناميكي بناءً على حمولة النظام وسلوك المستخدم
    """

    def allow_request(self, request, view):
        """
        Adjust rate limits based on current system conditions
        """
        if not request.user.is_authenticated:
            return True

        # Get system load factor (simplified)
        system_load = self.get_system_load()

        # Get user behavior score
        user_score = self.get_user_behavior_score(request.user)

        # Calculate dynamic rate limit
        base_rate = 1000  # Base requests per hour
        adjusted_rate = base_rate * (2 - system_load) * user_score

        # Apply the calculated rate
        cache_key = f"throttle_dynamic_{request.user.id}"
        now = time.time()
        requests = cache.get(cache_key, [])
        requests = [req_time for req_time in requests if now - req_time < 3600]

        if len(requests) >= adjusted_rate:
            return False

        requests.append(now)
        cache.set(cache_key, requests, 3600)

        return True

    def get_system_load(self):
        """
        Get current system load factor (0.5 = low load, 1.5 = high load)
        """
        # This is a simplified implementation
        # In production, you might check CPU usage, memory, database connections, etc.
        load_key = "system_load_factor"
        load = cache.get(load_key)

        if load is None:
            # Calculate load based on recent API usage
            recent_requests = cache.get("recent_api_requests", 0)
            if recent_requests < 100:
                load = 0.5  # Low load
            elif recent_requests < 500:
                load = 1.0  # Normal load
            else:
                load = 1.5  # High load

            cache.set(load_key, load, 300)  # Cache for 5 minutes

        return load

    def get_user_behavior_score(self, user):
        """
        Get user behavior score (0.5 = problematic user, 1.5 = good user)
        """
        # This is a simplified implementation
        # In production, you might analyze error rates, abuse patterns, etc.
        score_key = f"user_behavior_score_{user.id}"
        score = cache.get(score_key)

        if score is None:
            # Calculate score based on recent behavior
            if user.is_staff or user.is_superuser:
                score = 1.5  # Staff get higher limits
            else:
                # Check recent error rate
                error_rate = self.get_user_error_rate(user)
                if error_rate < 0.05:  # Less than 5% errors
                    score = 1.2
                elif error_rate < 0.15:  # Less than 15% errors
                    score = 1.0
                else:
                    score = 0.7  # High error rate, reduce limits

            cache.set(score_key, score, 1800)  # Cache for 30 minutes

        return score

    def get_user_error_rate(self, user):
        """
        Calculate user's recent error rate
        """
        # This would typically query your API usage logs
        # For now, return a default value
        return 0.05  # 5% error rate


class GracefulThrottle(BaseThrottle):
    """
    Throttle that provides graceful degradation instead of hard limits
    تحكم في المعدل يوفر تدهور تدريجي بدلاً من حدود صارمة
    """

    def allow_request(self, request, view):
        """
        Always allow requests but add delays for high-frequency users
        """
        if not request.user.is_authenticated:
            return True

        # Get recent request count
        cache_key = f"throttle_graceful_{request.user.id}"
        now = time.time()
        requests = cache.get(cache_key, [])
        requests = [req_time for req_time in requests if now - req_time < 3600]

        # Add delay based on request frequency
        if len(requests) > 500:  # High frequency
            time.sleep(2)  # 2 second delay
        elif len(requests) > 200:  # Medium frequency
            time.sleep(1)  # 1 second delay
        elif len(requests) > 100:  # Low-medium frequency
            time.sleep(0.5)  # 0.5 second delay

        # Always allow the request
        requests.append(now)
        cache.set(cache_key, requests, 3600)

        return True
