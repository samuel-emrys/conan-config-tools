from conan_config_tools import ROOT_DIR
from conan_config_tools import logger
from conan_config_tools import program_log
import logging
import configparser
import platform
import pathlib
import yaml

def set_remotes(ctx, **kwargs):
    """Configure the list of remotes for conan to use"""
    _set_log_verbosity(ctx.obj.get("verbosity"))

    program_log.debug(f"Context values: {ctx.obj}")
    program_log.debug(f"Keyword Arguments: {kwargs}")

    return


def set_profile(ctx, **kwargs):
    """Create a conan profile"""
    _set_log_verbosity(ctx.obj.get("verbosity"))

    program_log.debug(f"Context values: {ctx.obj}")
    program_log.debug(f"Keyword Arguments: {kwargs}")

    profile_name = kwargs["name"]
    profile_dir = pathlib.Path(ctx.obj.get("conan_home"), "profiles")
    profile_path = pathlib.Path(profile_dir, profile_name)

    if profile_path.exists():
        if not kwargs["force"]:
            program_log.critical(
                f"Profile '{profile_name}' already exists! Use -f to force."
            )
            return
        else:
            program_log.warning(f"Profile '{profile_name}' already exists! Overwriting.")

    default_fields = {
        "os": platform.system(),
        "os_build": platform.system(),
        "arch": _get_arch(),
        "arch_build": _get_arch(),
    }

    settings = kwargs["setting"]
    _validate_settings(ctx.obj.get("conan_home"), settings)

    for setting, value in default_fields.items():
        if setting not in settings.keys():
            settings[setting] = value

    config = configparser.ConfigParser()
    config["settings"] = settings
    config["options"] = kwargs["option"]
    config["build_requires"] = kwargs["build_requires"]
    config["env"] = kwargs["env"]
    config["conf"] = kwargs["conf"]
    config["buildenv"] = kwargs["buildenv"]

    try:
        profile_dir.mkdir(parents=True, exist_ok=True)
        with open(profile_path, "w") as profile:
            program_log.info(f"Writing profile '{profile_name}' to '{profile_path}'")
            config.write(profile, space_around_delimiters=False)
            program_log.info(f"Successfully wrote profile '{profile_name}' to '{profile_path}'")
    except:
        program_log.critical(f"Could not open file '{profile_path}'. Profile not written. Exiting.")

    return


def _validate_settings(conan_home, settings):
    settings_yml = {}
    settings_yml_path = pathlib.Path(conan_home, "settings.yml")
    try:
        with open(settings_yml_path, "r") as f:
            settings_yml = yaml.safe_load(f)
    except:
        program_log.warning(f"Could not open settings.yml: '{settings_yml_path}' does not exist. Settings not validated. Continuing.")
        return

    for key, value in settings.items():
        if key.split(".")[0] not in settings_yml.keys():
            raise ValueError(f"{key} not a valid setting.")

def _get_arch():
    arch = platform.machine()
    if arch == "AMD64":
        return "x86_64"
    return arch


def _set_log_verbosity(verbosity):
    # Set logging verbosity
    if verbosity or verbosity == 0:
        # Default console verbosity will be INFO level logging
        if verbosity == 0:
            logger.remove_handler(program_log, logging.StreamHandler)
        else:
            logger.adjust_handler_level(
                program_log, logging.StreamHandler, logging.DEBUG
            )
