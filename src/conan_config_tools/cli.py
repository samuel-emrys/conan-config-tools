import click
import conan_config_tools.application
import pathlib
import os


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(
        ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        case_sensitive=False,
    ),
    default="INFO",
    show_default=True,
    help="The level of logging to use",
)
@click.option(
    "-v", "verbosity", count=True, help="Increase the verbosity of the output"
)
@click.option("-q", "verbosity", flag_value=0, help="Suppress all output")
@click.option(
    "--conan-home",
    default=str(
        os.environ.get("CONAN_HOME", pathlib.Path(pathlib.Path.home(), ".conan2"))
    ),
    help="Path to the conan home directory.",
)
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj = kwargs


# @cli.command()
# @click.option(
#    "-n", "--name", type=str, required=True, help="The name to assign to the remote"
# )
# @click.option("-u", "--url", type=str, required=True, help="The URL of the remote")
# @click.option("--user", type=str, required=False, help="The user to authenticate as")
# @click.option("--token", type=str, required=False, help="The authentication token")
# @click.option(
#    "--config", type=str, required=False, help="The version of the site's API to use"
# )
# @click.pass_context
# def set_remote(ctx, **kwargs):
#    print(f"{kwargs=}")
#    conan_config_tools.application.set_remotes(ctx, **kwargs)


@cli.command()
@click.option("-n", "--name", type=str, required=True, help="The name of the profile")
@click.option(
    "-s", "--setting", type=str, required=False, multiple=True, help="A setting value."
)
@click.option(
    "-o", "--option", type=str, required=False, multiple=True, help="An option."
)
@click.option(
    "-c",
    "--conf",
    type=str,
    required=False,
    multiple=True,
    help="A configuration value.",
)
@click.option(
    "-tr",
    "--tool-requires",
    type=str,
    required=False,
    multiple=True,
    help="A tool requirement. This should be specified in the form pattern: reference, i.e. *: zlib/1.2.8",
)
@click.option(
    "-be",
    "--buildenv",
    type=str,
    required=False,
    multiple=True,
    help="A build environment variable.",
)
@click.option(
    "-re",
    "--runenv",
    type=str,
    required=False,
    multiple=True,
    help="A runtime environment variable.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force the profile to be written, ignore warnings and sanitize invalid values",
)
@click.pass_context
def set_profile(ctx, **kwargs):
    keyval_options = ["setting", "option", "conf", "runenv", "buildenv"]
    for option in keyval_options:
        kwargs[option] = keyval_tuple_to_dict(kwargs[option])
    kwargs["tool_requires"] = keyval_tuple_to_dict_of_lists(
        kwargs["tool_requires"], delimiter=":"
    )

    conan_config_tools.application.set_profile(ctx, **kwargs)


def keyval_tuple_to_dict(args: tuple, delimiter: str = "=") -> dict:
    if not args:
        return dict()
    return dict(arg.split(delimiter) for arg in args)


def keyval_tuple_to_dict_of_lists(args: tuple, delimiter: str = "=") -> dict:
    if not args:
        return dict()
    opts = {}
    for arg in args:
        key, value = arg.split(delimiter)
        value = value.strip()
        if key not in opts:
            opts[key] = [value]
            continue
        opts[key].append(value)
    return opts


if __name__ == "__main__":
    cli()
