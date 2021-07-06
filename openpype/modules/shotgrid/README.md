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

To pre-commit run the command:
```
pre-commit run
```

## Debugging

### VSCODE

* First install debugpy in poetry, to do this run this command in virtual env:
```pip install debugpy```

* Then set our debugging on remote attach with setting localhost and port 5678

* Place in file to debug this code:

```python
import debugpy

debugpy.listen(5678)
print("Waiting for debugger attach")
debugpy.wait_for_client()
debugpy.breakpoint()
print('break on this line')
```

You can now run the vscode debugger

### PYCHARM

...

## Rebase develop branch

To easily retrieve commits from branch develop to your working branch, do this command list in gitbash:
```bash
git checkout develop
git pull --rebase
git checkout add_shotgun_module
git rebase develop
git push --force
```
