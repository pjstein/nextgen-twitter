# nextgen/__init__.py


import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] [%(levelname)s] [%(funcName)s] [line: %(lineno)s] - %(message)s",
)