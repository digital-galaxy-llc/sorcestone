import os
import logging
from datetime import datetime


def get_log_path(log_file_name: str) -> str:
    """
    Generate a log file path based on the source file name.
    
    Args:
        source_file (str): Path to the source file
    
    Returns:
        str: Path to the log file
    """
    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create logs base directory
    logs_base_dir = os.path.join(os.path.dirname(__file__), '../../.logs')
    
    # Create date-specific subdirectory
    logs_date_dir = os.path.join(logs_base_dir, today)
    
    # Ensure the directory exists
    os.makedirs(logs_date_dir, exist_ok=True)
    
    # Convert source file name to log file name
    # Remove path, replace dots with underscores
    log_filename = os.path.basename(log_file_name).replace('.', '_') + '.log'
    
    return os.path.join(logs_date_dir, log_filename)


def setup_logger(log_level=logging.INFO) -> logging.Logger:
    """
    Set up a logger for a specific source file.
    
    Args:
        log_level (int, optional): Logging level. Defaults to logging.INFO.
    
    Returns:
        logging.Logger: Configured logger
    """
    
    source_file = "convertor"
    # Get log file path
    log_path = get_log_path(source_file)
    
    # Create logger
    logger = logging.getLogger(os.path.basename(source_file))
    logger.setLevel(log_level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logger()