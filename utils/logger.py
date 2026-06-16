import logging
from pathlib import Path
from config.settings import LOG_LEVEL


def get_logger(name: str) -> logging.Logger:  # object
    """Create a configured logger."""

    logger = logging.getLogger(name) # This doesn't create a new logger — it retrieves one
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Don't add handlers if they already exist
    if logger.handlers:
        return logger

    # Format: timestamp - name - level - message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler 1: Console (same as print, but better)
    console_handler = logging.StreamHandler() # StreamHandler — prints to terminal. Same as print() but with timestamps and levels
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler) # addHandler() wires it to the logger

    # Handler 2: File (audit trail!)
    log_dir = Path(__file__).parent.parent / 'data' / 'output' # the logger.py file itself
    log_dir.mkdir(parents=True, exist_ok=True) # creates the folder if it doesn't exist, no crash if it already does
    file_handler = logging.FileHandler(log_dir / 'pipeline.log') # FileHandler — writes to data/output/pipeline.log. Every run appends to this file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

