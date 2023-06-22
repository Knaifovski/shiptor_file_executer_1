import loguru

logger = loguru.logger
path_to_file = "logs/"
format = "{time}|{level}|{message}"

logger.add(f"{path_to_file}info.json", format=format, level="INFO", rotation="1 day",
           compression="zip", serialize=True)

logger.add(f"{path_to_file}debug.json", format=format, level="DEBUG", rotation="1 day",
           compression="zip", serialize=True)

logger.add(f"{path_to_file}warning.json", format=format, level="WARNING", rotation="1 week",
           compression="zip", serialize=True)

logger.add(f"{path_to_file}error.json", format=format, level="ERROR", rotation="1 month",
           compression="zip", serialize=True)
