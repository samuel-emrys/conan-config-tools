# conan-config-tools

`conan-config-tools` is a project to facilitate the configuration of conan when using continuous integration tools. The primary need for this arose out of a desire to minimise unnecessary duplication of build logic over different operating systems.


## Installation

```bash
$ pip install conan-config-tools
```

## Usage

```bash
$ cct --help
Usage: cct [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level [NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  The level of logging to use  [default: INFO]
  -v                              Increase the verbosity of the output
  -q                              Suppress all output
  --conan-home TEXT               Path to the conan home directory.
  --help                          Show this message and exit.

Commands:
  set-profile
```


## Development

```bash
$ pip install -e '.[dev]'
```
