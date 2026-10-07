import logging
import time

logger = logging.getLogger(__name__)

def timer(f): # Decorator function to log time elapsed during function.
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return f(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.info(f"{f.__name__} took {elapsed:.2f} seconds")
    return wrapper