import logging

def get_gemini_logger(name: str = "gemini_sdk") -> logging.Logger:
    """! Returns a configured logger instance for the Gemini SDK."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
