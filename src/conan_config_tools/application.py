import io
import logging
import pathlib
import re
from contextlib import redirect_stderr

from conan.api.conan_api import ConanAPI
from conan.api.subapi.profiles import ProfilesAPI
from conan.tools.env.environment import ProfileEnvironment
from conans.client.profile_loader import _profile_parse_args
from conans.errors import ConanException
from conans.model.profile import Profile
from conans.model.settings import Settings
from conans.util.files import save

from conan_config_tools import logger, program_log


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

    conan_home = pathlib.Path(ctx.obj.get("conan_home")).resolve()
    profile_name = kwargs["name"]
    profile_dir = pathlib.Path(conan_home, "profiles")
    profile_path = pathlib.Path(profile_dir, profile_name)

    if profile_path.exists():
        if not kwargs["force"]:
            program_log.critical(
                f"Profile '{profile_name}' already exists! Use -f to force."
            )
            return
        else:
            program_log.warning(
                f"Profile '{profile_name}' already exists! Overwriting."
            )

    # Transform arguments to {'settings': ["compiler=gcc", "compiler.version=11"]} format
    args = {
        "settings": _dict_to_keyval_list(kwargs["setting"], delimiter="="),
        "options": _dict_to_keyval_list(kwargs["option"], delimiter="="),
        "conf": _dict_to_keyval_list(kwargs["conf"], delimiter="="),
    }
    buildenv = _dict_to_keyval_list(kwargs["buildenv"], delimiter="=")
    runenv = _dict_to_keyval_list(kwargs["runenv"], delimiter="=")
    program_log.debug(f"Conan args: {args}")

    conan_api = ConanAPI(cache_folder=conan_home)

    f = io.StringIO()
    with redirect_stderr(f):
        base_profile = conan_api.profiles.detect()

    # Construct a profile from the base detected profile
    profile = Profile()
    profile.compose_profile(base_profile)
    args_profile = _profile_parse_args(**args)
    # Add command line specified arguments to the profile
    profile.compose_profile(args_profile)
    # Make sure the conf settings in the profile are valid
    profile.conf.validate()

    # Load conan_home/extensions/plugins/profile.py to validate cppstd
    profile_api = ProfilesAPI(conan_api)
    profile_plugin = profile_api._load_profile_plugin()
    if profile_plugin is not None:
        profile_plugin(profile)
    # Ensure the settings specified in the profile are valid or sanitized
    cache_settings = conan_api.config.settings_yml
    _validate_settings(profile, cache_settings, kwargs["force"])

    # Append environment information to profile
    profile.buildenv = ProfileEnvironment.loads("\n".join(buildenv))
    profile.runenv = ProfileEnvironment.loads("\n".join(runenv))
    # Add tool_requires patterns to profile
    for pattern, references in kwargs["tool_requires"].items():
        profile.tool_requires[pattern] = references
    program_log.debug(f"{profile}")
    # Save profile to disk
    save(profile_path, profile.dumps())
    program_log.info(f"Successfully wrote profile '{profile_name}' to '{profile_path}'")
    return


def _validate_settings(profile: Profile, cache_settings: Settings, force: bool):
    """Ensure that the settings in the provided profile are consistent with settings.yml in the cache.

    :param profile: The profile to validate
    :type profile: `Profile`
    :param cache_settings: The settings from the client cache
    :type cache_settings: `Settings`
    :param force: A boolean flag indicating whether invalid settings should be sanitized or not. True
    indicates that invalid values will be removed from the profile.
    :type force: bool
    """
    while True:
        try:
            profile.process_settings(cache_settings)
            break
        except ConanException as e:
            if not force:
                program_log.critical(f"{e}. Use `-f` to force removal of invalid keys.")
                raise ValueError(e)
            else:
                profile.processed_settings = None
                erroneous_attribute = re.search(r"settings(.\w+)+", str(e)).group()
                key_to_remove = ".".join(erroneous_attribute.split(".")[1:])
                program_log.warning(e)
                program_log.warning(f"Removing invalid key '{key_to_remove}'.")
                profile.settings.pop(key_to_remove)


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


def _dict_to_keyval_list(values: dict, delimiter: str):
    return [f"{k}{delimiter}{v}" for k, v in values.items()]
