import logging


def setup_logger(log_file: str = "sms-log.log") -> logging.Logger:
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger()


logger = setup_logger()
