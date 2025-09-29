# Contributing
## Getting Started

1. [Create a fork](https://guides.github.com/activities/forking/#fork) of build-the-bot

2. Clone the forked repo locally

```console
$ git clone https://github.com/Viasat/build-the-bot.git
```

3. Create a virtualenv and activate it:
```console
$ python3 -m venv venv
$ source venv/bin/activate
```
Or on Windows cmd:
```console
$ python3 -m venv venv
$ venv\Scripts\activate
```
4. Install build_the_bot
```console
$ pip install build_the_bot
```

4. Run the tests to make sure everything is working right:

```console
$ python -m pip install pytest pytest-cov
$ pytest --cov=build_the_bot --cov-report=term-missing --cov-fail-under=100
```

## Commiting Changes

build-the-bot uses the semantic release tool to automatically generate releases. Your commit message must follow the format below. If your not changing any of the package code, use "skip release" in your commit message to skip building a new version.   

```
Commit Prefix |  Major.Minor.Patch |  Intended use
--------------|--------------------|----------------------------------------
 'Breaking:'  |        Major       |  Backwards-incompatible feature change
 'Update:'    |        Minor       |  Backwards-compatible feature change
 'New:'       |        Minor       |  New feature
 'Fix:'       |        Patch       |  Feature fix
 'Docs:'      |        Patch       |  Documentation
 'Build:'     |        Patch       |  Build process changes
 'Upgrade:'   |        Patch       |  Dependency upgrade
 'Chore:'     |        Patch       |  Housekeeping chores
```

## Creating a Pull Request
### Expectations
- You added unit tests for your code.
- All unit tests pass.
- You performed some sort of integration testing. Use the provided example, if needed.
- Coverage is still 100%. Use `# pragma: no cover` sparingly for code that does not require coverage.
- Any new classes, methods or functions have [docstrings in Sphinx style](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html#the-sphinx-docstring-format).
- The coding conventions listed below are followed.


## Coding Conventions
* File names: lower_case_with_underscores.py
* Class names: class UpperCamelCase():
* Function names: def lowerCamelCase():
* Variable names:
   * members of a class: m_lowerCamelCase
   * global variables: g_lowerCamelCase
   * local variables: lowerCamelCase