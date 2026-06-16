import time
from functools import wraps
from utils.logger import get_logger

logger = get_logger('timer')

def timer(func):
    """Measure how long a function takes."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()  # timestamp in seconds.
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f" ⏱ {func.__name__} took {elapsed: .2f}s")
        return result
    return wrapper
