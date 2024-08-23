import logging


def setup_logging():
    from .core.consts import settings

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S%p'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(settings.log_filepath)
    file_handler.setLevel(logging.WARNING)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S%p'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.info('logger was setup')