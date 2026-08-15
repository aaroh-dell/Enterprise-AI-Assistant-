import time
import requests
from backend.logger import logger


def call_with_retry(func, *args, max_attempts=3, delay_seconds=1, **kwargs):
    """
    Calls func(*args, **kwargs), retrying on network/connection failures.
    Returns the function's result, or a fallback error dict if all attempts fail.
    """
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_error = e
            logger.warning(f"Attempt {attempt}/{max_attempts} failed: {e}")
            if attempt < max_attempts:
                time.sleep(delay_seconds)
        except Exception as e:
            # Non-network errors (bad JSON, etc.) - don't retry, just log and fail
            logger.error(f"Non-retryable error: {e}")
            return {"error": f"Something went wrong: {str(e)}"}

    logger.error(f"All {max_attempts} attempts failed. Last error: {last_error}")
    return {"error": "The service is temporarily unavailable. Please try again shortly."}
