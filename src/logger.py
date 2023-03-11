import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
