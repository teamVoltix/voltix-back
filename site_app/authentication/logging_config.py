import logging
from logging.handlers import RotatingFileHandler

# Define the logging configuration for the authentication app
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create a handler for writing logs to a file
file_handler = RotatingFileHandler(
    filename="authentication_logs.log",  # Log file name
    maxBytes=1024 * 1024 * 5,            # Maximum file size (5MB)
    backupCount=3,                       # Number of backup files to keep
)
file_handler.setLevel(logging.WARNING)   # Set log level for the handler
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configure the logger
logger = logging.getLogger("authentication")
logger.setLevel(logging.WARNING)         # Set the minimum level of logs to capture
logger.addHandler(file_handler)
