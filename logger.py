import logging
import logging.handlers
import os
from datetime import datetime
from config import Config

class CustomLogger:
    def __init__(self):
        # Create logs directory if not exists
        log_dir = os.path.join(Config.WORK_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup main logger
        self.logger = logging.getLogger('AII_BOT')
        self.logger.setLevel(logging.DEBUG)
        
        # Log file path with date
        log_file = os.path.join(
            log_dir, 
            f'bot_{datetime.now().strftime("%Y%m%d")}.log'
        )
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatters
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def critical(self, message):
        self.logger.critical(message)

# Initialize global logger
LOGGER = CustomLogger()
