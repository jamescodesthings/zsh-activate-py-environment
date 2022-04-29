# Add this directory to PATH env s.t. we can call the python script form anywhere
PATH=$(dirname "$0"):$PATH

function activate_py_environment_if_existing()
{
    deactivate_py_environment
    COMMAND="$(zsh-activate-py-environment.py "activate")"

    CHECK_CONDA=${COMMAND:0:14}
    CONDA_ENV=${COMMAND:15}
    if [[ "$CHECK_CONDA" == "conda activate" ]]; then
      eval $COMMAND &>/dev/null

      if [[ $? -ne 0 ]]; then
        echo "Could not activate environment, create it with"
        echo "conda env create -f [path_to_environment.yml]"
        return 1
      fi
    fi

    eval $(zsh-activate-py-environment.py "activate")
}

function deactivate_py_environment()
{
    eval $(zsh-activate-py-environment.py "deactivate")
}

function link_py_environment()
{
    zsh-activate-py-environment.py "link" "$@"
    if [ $? -eq 0 ]; then
        activate_py_environment_if_existing
    fi
}

function unlink_py_environment()
{
    deactivate_py_environment
    zsh-activate-py-environment.py "unlink"
}

autoload -Uz add-zsh-hook
add-zsh-hook -D chpwd activate_py_environment_if_existing
add-zsh-hook chpwd activate_py_environment_if_existing
