import hashlib
from db.redis import initialize_redis

class RedisAgent:
    def __init__(self, clear_cache):
        """
        Initialize the RedisAgent with connection details.
        
        Args:
            host (str): Redis server hostname.
            port (int): Redis server port.
            db (int): Redis database index.
        """
        self.client = initialize_redis()
        if clear_cache:
            self.clear_cache()
        
    
    def _generate_cache_key(self, question: str) -> str:
        """
        Generate a unique cache key for a given question using its hash.
        
        Args:
            question (str): The user question.
        
        Returns:
            str: A hashed key for the question.
        """
        return hashlib.sha256(question.encode()).hexdigest()

    def check_cache(self, question: str) -> str | None:
        """
        Check if the question has a cached response in Redis.
        
        Args:
            question (str): The user question.
        
        Returns:
            str: Cached response if found, otherwise None.
        """
        key = self._generate_cache_key(question)
        cached_response = self.client.get(key)
        if cached_response:
            return cached_response
        return None

    def store_cache(self, question: str, response: str, ttl=3600):
        """
        Store a question-response pair in the Redis cache.
        
        Args:
            question (str): The user question.
            response (str): The response to be cached.
            ttl (int): Time-to-live for the cache entry in seconds.
        """
        key = self._generate_cache_key(question)
        self.client.set(key, response, ex=ttl)

    def clear_cache(self):
        """
        Clear all entries in the Redis cache.
        """
        self.client.flushdb()
        print("Redis cache cleared.")