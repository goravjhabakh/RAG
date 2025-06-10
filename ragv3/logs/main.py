import logging
from typing import Optional
import sys

class LOGGER:
    instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, file_path:str = 'logs/latest.log') -> logging.Logger:
        if cls.instance is None:
            logger = logging.getLogger('main_logger')
            logger.setLevel(logging.DEBUG)
            logger.propagate = False

            # formatting logs
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # Logging to console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # Logging to file
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            cls.instance = logger
        return cls.instance