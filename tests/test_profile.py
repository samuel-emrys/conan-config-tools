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

@pytest.fixture()
def mock_conan_home():
    conan_home = pathlib.Path(".conan")
    profile_dir = pathlib.Path(conan_home, "profiles")
    profile_dir.mkdir(parents=True, exist_ok=True)
    settings_yml = pathlib.Path(pathlib.Path(__file__).parent.absolute(), "resources", "settings.yml")
    shutil.copy(src=settings_yml, dst=conan_home)
    yield conan_home
    shutil.rmtree(conan_home)

@pytest.fixture()
def mock_existing_profile(mock_conan_home):
    profile = pathlib.Path(mock_conan_home, "profiles", "test")

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

    yield profile


def test_profile_exists_does_not_throw_when_forced(caplog, mock_conan_home, mock_existing_profile):
    # cct -v --conan-home . set-profile -f -n test -s build_type=Debug

    # Invoke the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["-v", "--conan-home", mock_conan_home, "set-profile", "-f", "-n", "test", "-s", "build_type=Debug"])

    # No error in exit code
    assert result.exit_code == 0
    # No critical error messages
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
    # The application is overwriting a profile
    assert "Profile 'test' already exists! Overwriting." in [r.msg for r in caplog.records]


def test_profile_does_not_exist_does_not_throw(caplog, mock_conan_home):
    # cct -v --conan-home . set-profile -f -n test -s build_type=Debug
    # Invoke the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["-v", "--conan-home", mock_conan_home, "set-profile", "-n", "test", "-s", "build_type=Debug"])

    assert result.exit_code == 0
    for record in caplog.records:
        assert record.levelname != "CRITICAL"

def test_invalid_setting_is_sanitized_from_profile_when_forced(caplog, mock_conan_home):
    # cct -v --conan-home . set-profile -f -n test -s compiler="Visual Studio" -s compiler.libcxx=""
    # Invoke the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["-v", "--conan-home", mock_conan_home, "set-profile", "-f", "-n", "test", "-s", "compiler=Visual Studio", "-s", "compiler.libcxx="])

    assert result.exit_code == 0
    for record in caplog.records:
        assert record.levelname != "CRITICAL"

    profile = pathlib.Path(mock_conan_home, "profiles", "test")
    config = configparser.ConfigParser()
    config.read(profile)

    # Profile should not contain compiler.libcxx key
    with pytest.raises(Exception) as exc:
        config.get("settings", "compiler.libcxx")


def test_invalid_setting_throws(caplog, mock_conan_home):
    # cct -v --conan-home . set-profile  -n test -s compiler="Visual Studio" -s compiler.libcxx=libstdc++11
    # Invoke the CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["-v", "--conan-home", mock_conan_home, "set-profile", "-n", "test", "-s", "compiler=Visual Studio", "-s", "compiler.libcxx=libstdc++11"])

    assert result.exit_code == 1 # ValueError
    # Invalid configuration should cause a critical error when not forced
    assert "CRITICAL" in [r.levelname for r in caplog.records]
    assert "'compiler.libcxx' is not a valid setting for compiler Visual Studio! Force removal of invalid keys with -f" in [r.msg for r in caplog.records]

# def test_valid_profile_does_not_throw(caplog):
#     assert False
# 
# def test_invalid_option_throws(caplog):
#     assert False
# 
# def test_invalid_conf_throws():
#     assert False
