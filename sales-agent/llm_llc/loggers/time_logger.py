import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler()
log_filename = "llmllc-sales-timed-output.log"
file_handler = logging.FileHandler(filename=log_filename)
handlers = [stream_handler, file_handler]


class TimeFilter(logging.Filter):
    def filter(self, record):
        return "Running" in record.getMessage()


logger.addFilter(TimeFilter())

# Configure the logging module
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s %(asctime)s - %(levelname)s - %(message)s",
    handlers=handlers,
)


def time_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)  # Function execution
        elapsed_time = time.time() - start
        logger.info(f"Running {func.__name__}: --- {elapsed_time} seconds ---")
        return result

    return wrapper
