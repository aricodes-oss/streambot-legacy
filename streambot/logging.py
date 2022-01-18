import logging
from streambot import env

level = getattr(logging, env.str("LOGLEVEL", default="INFO").upper(), None)
logger = logging.getLogger("streambot")

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(level)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

logger.setLevel(level)
