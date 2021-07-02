## Getting started

### First steps

At the beginning you have to create a working environment, you can achieve it with bootstrap scripts from `tools` folder. Just follow the tutorial from the main `README.md` [file](../../../README.md).

### Hooks

You will need to install followed packages:
  - pre-commit
  - black
  - mypy

```bash
pip install pre-commit black mypy
```
In order to make pre-commit work within the project you need to activate it at the root level.

```bash
pre-commit install
```
At the end you are supposed to see a message as below:
```
pre-commit installed at .git/hooks/pre-commit
```
Pre-commit will check your code style and formatting. You can configure the IDE of your choice to be able to use `pre-commit` and/or `black` formatter.
