import pytest
import configparser
import platform
import os
import pathlib
import shutil
from mock import patch, mock_open
from conan_config_tools import application
from conan_config_tools.cli import cli
from click.testing import CliRunner


def test_profile_exists_does_not_throw_when_forced(caplog):
    # cct -v --conan-home . set-profile -f -n test -s build_type=Debug
    profile_dir = pathlib.Path("profiles")
    profile_dir.mkdir(parents=True, exist_ok=True)
    profile = pathlib.Path(profile_dir, "test")

    # Dummy profile
    config = configparser.ConfigParser()
    config["settings"] = {
        "os": platform.system(),
        "os_build": platform.system(),
        "arch": application._get_arch(),
        "arch_build": application._get_arch(),
    }

    # Populate an existing profile
    with profile.open("w") as f:
        config.write(f, space_around_delimiters=False)

    # Invoke the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["-v", "--conan-home", ".", "set-profile", "-f", "-n", "test", "-s", "build_type=Debug"])

    # Clean up after test
    shutil.rmtree(profile_dir)
    # No error in exit code
    assert result.exit_code == 0
    # No critical error messages
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
    # The application is overwriting a profile
    assert "Profile 'test' already exists! Overwriting." in [r.msg for r in caplog.records]


def test_profile_does_not_exist_does_not_throw(caplog):
    # cct -v --conan-home . set-profile -f -n test -s build_type=Debug
    # Invoke the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["-v", "--conan-home", ".", "set-profile", "-n", "test", "-s", "build_type=Debug"])

    assert result.exit_code == 0
    for record in caplog.records:
        assert record.levelname != "CRITICAL"


# def test_valid_profile_does_not_throw(caplog):
#     assert False
# 
# 
# def test_invalid_setting_throws(caplog):
#     assert False
# 
# 
# def test_invalid_option_throws(caplog):
#     assert False
# 
# 
# def test_invalid_conf_throws():
#     assert False
