# zsh-activate-py-environment
ZSH plugin that automagically detects and activates your python environments (poetry, virtualenv, conda) while traversing directories.

# Usage
```bash
source zsh-activate-py-environment.plugin.zsh
cd into a directory with an environment
```

If it does not work as expected, you do `link_py_environment [type] [name]` to create a .linked_env which will then definitely work.

If you need to unlink you do `unlink_py_environment`.

