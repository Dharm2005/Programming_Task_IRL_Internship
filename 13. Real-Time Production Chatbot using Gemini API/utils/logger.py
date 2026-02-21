from loguru import logger

logger.add(
    "logs/app.log",
    rotation="1 MB",
    level="INFO"
)

def get_logger():
    return logger
