import logging

# LOG_LEVEL = logging.ERROR
LOG_LEVEL = logging.DEBUG
# LOG_LEVEL = logging.INFO

def make_logger(mod_name, log_level=LOG_LEVEL):
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s:(%(module)s/%(name)s): "%(message)s"')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger
