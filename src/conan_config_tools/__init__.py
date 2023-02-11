import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
PROGRAM_NAME = __name__

from conan_config_tools.logger import configure_logger  # noqa: E402

program_log = configure_logger()

