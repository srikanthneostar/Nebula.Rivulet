from logs.logs import get_fabric_logger


def main():
    logger = get_fabric_logger(__name__, "C:/Temp/test.log")
    logger.info("This is a test log message.")
    logger.warning("This is a warning message.")

main()