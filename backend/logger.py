import logging
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("enterprise_assist")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # File handler - writes everything to a persistent log file
    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Console handler - still shows in your terminal like before
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)