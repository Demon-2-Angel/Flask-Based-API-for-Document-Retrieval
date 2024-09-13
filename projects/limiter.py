from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

# Configure Redis for rate-limiting
redis_connection = Redis(host='localhost', port=6379)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)
