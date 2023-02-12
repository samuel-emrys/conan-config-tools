from conan_config_tools import ROOT_DIR
from conan_config_tools import logger
from conan_config_tools import program_log
import logging
import configparser
import copy
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

    settings = _validate_settings(ctx.obj.get("conan_home"), kwargs["setting"], kwargs["force"])
    program_log.debug(f"{settings=}")

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


def _validate_settings(conan_home, settings, force):
    settings_yml = {}
    settings_yml_path = pathlib.Path(conan_home, "settings.yml")
    if not settings_yml_path.exists():
        user_settings_yml_path = settings_yml_path
        settings_yml_path = pathlib.Path(pathlib.Path.home(), ".conan", "settings.yml")
        program_log.warning(f"settings.yml does not exist in the user specified conan home '{user_settings_yml_path}'. Attempting to fall back to '{settings_yml_path}'")
    try:
        with open(settings_yml_path, "r") as f:
            settings_yml = yaml.safe_load(f)
            program_log.debug(f"Successfully loaded settings from '{settings_yml_path}'")
    except:
        program_log.warning(f"Could not open settings.yml: '{settings_yml_path}' does not exist. Settings not validated. Continuing.")
        return settings

    for key, value in list(settings.items()):
        key_list = key.split(".")
        if len(key_list) > 1 and "compiler" in key_list:
            key_list.insert(1, settings["compiler"])
        settings_values = _get_value(key_list, settings_yml)
        if not settings_values:
            invalid_setting_msg = f"'{key}' is not a valid setting for compiler {settings['compiler']}!"
            if not force:
                program_log.critical(f"{invalid_setting_msg} Force removal of invalid keys with -f")
                raise ValueError(f"{invalid_setting_msg} Force removal of invalid keys with -f")
            invalid_setting_msg = f"{invalid_setting_msg} Sanitizing '{key}' from profile."
            program_log.warning(invalid_setting_msg)
            del settings[key]
        else:
            if isinstance(settings_values, dict):
                settings_values = list(settings_values.keys())
            if value not in settings_values:
                program_log.warning(f"'{key}' has an invalid value! {value} is not one of '{settings_values}'")
            else:
                program_log.debug(f"'{key}={value}' successfully validated")
    return settings

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

def _get_value(key_list, dict_):
    reduced = copy.deepcopy(dict_)
    for key in key_list:
        if reduced:
            reduced = reduced.get(key)
    return reduced
