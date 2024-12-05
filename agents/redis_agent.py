import redis
import hashlib

class RedisAgent:
    def __init__(self, host="localhost", port=6379, db=0):
        """
        Initialize the RedisAgent with connection details.
        
        Args:
            host (str): Redis server hostname.
            port (int): Redis server port.
            db (int): Redis database index.
        """
        self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
    
    def _generate_cache_key(self, question: str) -> str:
        """
        Generate a unique cache key for a given question using its hash.
        
        Args:
            question (str): The user question.
        
        Returns:
            str: A hashed key for the question.
        """
        return hashlib.sha256(question.encode()).hexdigest()

    def check_cache(self, question: str) -> str:
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
            print(f"Cache hit for question: {question}")
        else:
            print(f"Cache miss for question: {question}")
        return cached_response

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
        print(f"Cached response for question: {question}")
