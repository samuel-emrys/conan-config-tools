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

```bash
$ cct set-profile --help
Usage: cct set-profile [OPTIONS]

Options:
  -n, --name TEXT            The name of the profile  [required]
  -s, --setting TEXT         A setting value.
  -o, --option TEXT          An option.
  -c, --conf TEXT            A configuration value.
  -tr, --tool-requires TEXT  A tool requirement. This should be specified in
                             the form pattern: reference, i.e. *: zlib/1.2.8
  -be, --buildenv TEXT       A build environment variable.
  -re, --runenv TEXT         A runtime environment variable.
  -f, --force                Force the profile to be written, ignore warnings
                             and sanitize invalid values
  --help                     Show this message and exit.
```


### Windows Example

```bash
$ cct --log-level=DEBUG --conan-home=.custom-conan-home set-profile -n msvc193 -s compiler=msvc -s compiler.version=193 -s compiler.libcxx=libstdc++11 -o armadillo:use_lapack=openblas -tr *:zlib/1.2.8 -tr *:cmake/3.25.1 -tr armadillo:gcc/12.2.0 -be TZ_DATA_DIR=C:\Users\user\data -re RES_DIR=C:\Users\user\res -f
```

This will result `.custom-conan-home/profiles/msvc193` being created with the following contents:

```
[settings]
os=Windows
arch=x86_64
compiler=msvc
compiler.version=193
[options]
armadillo:use_lapack=openblas
[conf]
[tool_requires]
*: zlib/1.2.8, cmake/3.25.1
armadillo: gcc/12.2.0
[buildenv]
TZ_DATA_DIR=C:\Users\user\data
[runenv]
RES_DIR=C:\Users\user\res
```

Note that because the `-f` flag has been passed, the invalid setting `compiler.libcxx` has been sanitized from the resulting profile.


## Development

### Installation

```bash
$ pip install -e '.[dev]'
```

### Running the tests

```bash
$ pytest -vs
```
