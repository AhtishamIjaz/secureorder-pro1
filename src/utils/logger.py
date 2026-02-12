import logging
import sys

def setup_logger(name: str):
    logger = logging.getLogger(name)
    
    # Only add handlers if they don't exist to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Format: [Time] [Project Name] [Level] Message
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Output to terminal
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

# Create a master logger for the whole system
system_logger = setup_logger("secureorder-pro")