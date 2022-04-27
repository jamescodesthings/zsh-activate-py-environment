#!/usr/bin/env python3

from argparse import ArgumentParser
from asyncio.log import logger
from os import environ, getcwd, listdir, remove
from os.path import abspath, isdir, isfile, join, split
from shutil import which
from sys import stderr, argv

##########################
##### Some Constants #####

# If True prints __print_debug statements
DEBUG = True

CONDA_TYPE = "conda"
VENV_TYPE = "venv"
POETRY_TYPE = "poetry"
LINKED_TYPE = "linked"

SUPPORTED_ENVIRONMENT_TYPES = [CONDA_TYPE, VENV_TYPE, POETRY_TYPE]

LINKED_ENV_FILES = [".linked_env"]
POETRY_FILES = ["poetry.lock"]
VENV_FILES = ["venv", ".venv"]
CONDA_FILES = ["environment.yaml"]

TYPE_TO_FILES = {
    LINKED_TYPE: LINKED_ENV_FILES,
    POETRY_TYPE: POETRY_FILES,
    VENV_TYPE: VENV_FILES,
    CONDA_TYPE: CONDA_FILES,
}

FILE_TO_TYPE = {
    environment_file: type
    for type, environment_files_list in TYPE_TO_FILES.items()
    for environment_file in environment_files_list
}


##########################
##### Main Functions #####

def main():
    # TODO: add custom print usage function
    parser = ArgumentParser(
        description="Automagically detect and activate python environments (poetry, virtualenv, conda)"
    )
    subparsers = parser.add_subparsers()

    # activate command
    parser_activate = subparsers.add_parser("activate")
    parser_activate.set_defaults(command_function=activate)

    # deactivate command
    parser_activate = subparsers.add_parser("deactivate")
    parser_activate.set_defaults(command_function=deactivate)

    # link command
    parser_link = subparsers.add_parser("link")
    parser_link.set_defaults(command_function=link)

    parser_link.add_argument("environment_type", choices=[VENV_TYPE, CONDA_TYPE])
    parser_link.add_argument("name_or_path", type=str)

    # unlink command
    parser_unlink = subparsers.add_parser("unlink")
    parser_unlink.set_defaults(command_function=unlink)

    args = parser.parse_args()
    args_without_filename = argv[1:]
    quoted_args = [f'"{arg}"' for arg in args_without_filename]
    as_log_message = ', '.join(quoted_args)
    __print_debug(f"main({as_log_message})")
    args.command_function(
        # call given command function with parameters
        **{
            parameter: value
            for parameter, value in vars(args).items()
            if parameter != "command_function"
        }
    )


def activate():
    __print_debug("activate()")
    type_and_environment_file = __find_nearest_environment_file()

    if type_and_environment_file:
        __handle_environment_file(type_and_environment_file[0], type_and_environment_file[1])


def deactivate():
    __print_debug("deactivate()")
    conda_environment_name = environ.get("CONDA_DEFAULT_ENV", "")

    if environ.get("VIRTUAL_ENV", ""):
        __return_command("deactivate")

    # Do not deactivate conda base environment.
    # TODO: expose possibility to change this
    elif conda_environment_name:
        if conda_environment_name != "base":
            __return_command("conda deactivate")


def link(environment_type, name_or_path):
    __print_debug(f"link(\"{environment_type}\", \"{name_or_path}\")")
    if any([linked_env_file in listdir() for linked_env_file in LINKED_ENV_FILES]):
        raise Exception(
            "This directory is already linked! You can remove this by using 'unlink_py_environment'"
        )

    if environment_type == VENV_TYPE:
        with open(LINKED_ENV_FILES[0], "w") as file:
            file.write(f"{environment_type};{abspath(name_or_path)}")
    
    elif environment_type == CONDA_TYPE:
        with open(LINKED_ENV_FILES[0], "w") as file:
            file.write(f"{environment_type};{name_or_path}")


def unlink():
    __print_debug(f"unlink()")
    linked_files_in_working_directory = [file for file in LINKED_ENV_FILES if isfile(file)]

    if linked_files_in_working_directory:
        for file in linked_files_in_working_directory:
            remove(file)
    else:
        __print_information(
            f"No file found that explicitely links this directory, looked for: {', '.join(LINKED_ENV_FILES)}"
        )


############################
##### Helper Functions #####


def __print_debug(message):
    if DEBUG:
        print(message, file=stderr)

def __print_information(message):
    print(message, file=stderr)


def __return_command(shell_command):
    print(shell_command)


def __find_nearest_environment_file(
    directory=getcwd(), priority=[LINKED_TYPE, POETRY_TYPE, VENV_TYPE, CONDA_TYPE]
):
    __print_debug(f"__find_nearest_environment_file(\"{directory}\", {priority})")
    if any([environment_type not in TYPE_TO_FILES.keys() for environment_type in priority]) or any(
        [type(environment_type) != str for environment_type in priority]
    ):
        raise ValueError(
            f"Only the following environment types (given as `str`) are supported! - {', '.join(TYPE_TO_FILES.keys())}"
        )

    if not isdir(directory):
        raise ValueError("Parameter `directory` need to be a valid directory!")

    directory_content = listdir(directory)

    # iterate over list of lists that contain the actual files to look for
    for environment_files_list in [TYPE_TO_FILES[type] for type in priority]:
        for environment_file in environment_files_list:
            if environment_file in directory_content:
                return FILE_TO_TYPE[environment_file], join(directory, environment_file)

    parent_directory, not_root_directory = split(directory)
    if not_root_directory:
        return __find_nearest_environment_file(directory=parent_directory, priority=priority)
    else:
        return None


def __parse_linked_environment_file(linked_environment_file):
    __print_debug(f"__parse_linked_environment_file(\"{linked_environment_file}\")")
    if not isfile(linked_environment_file):
        raise ValueError(
            f"Found linked environment file ist not a file. Check: {linked_environment_file}"
        )

    try:
        with open(linked_environment_file, "r") as file:
            environment_type, environment_path_or_name = file.read().split(";")
    except:
        raise Exception(
            f"Something went wrong! Is the linked environment file malformed? - Check: {linked_environment_file}"
        )

    if environment_type not in SUPPORTED_ENVIRONMENT_TYPES:
        raise Exception(
            f"The given environment type in the linked environment file is not supported. Type: {environment_type} found in: {linked_environment_file}"
        )

    return environment_type.strip(), environment_path_or_name.strip()


def __check_dependencies(command):
    __print_debug(f"__check_dependencies(\"{command}\")")
    if which(command):
        return True
    else:
        __print_information(f"Necessary dependency '{command}' not installed, omiting this!")
        return False


def __print_activation_message(environment_type):
    __print_debug(f"__print_activation_message(\"{environment_type}\")")
    __print_information(f"\n🐍 Try to activate '{environment_type}' environment ...\n")


def __handle_environment_file(type, environment_file_or_name):
    __print_debug(f"__handle_environment_file(\"{type}\", \"{environment_file_or_name}\")")
    if type == LINKED_TYPE:
        # either path to poetry/virtualenv or conda environment name.
        environment_type, environment_path_or_name = __parse_linked_environment_file(
            environment_file_or_name
        )

        # TODO:How to handle conda? we get name here but use path..
        __handle_environment_file(environment_type, environment_path_or_name)

    elif type == POETRY_TYPE:
        if __check_dependencies(POETRY_TYPE):
            # poetry does not need the `environment_file`. It handle this by itself.
            __return_command("source $(poetry env info --path)/bin/activate")
            __print_activation_message(type)

    elif type == VENV_TYPE:
        __return_command(f"source {environment_file_or_name}/bin/activate")
        __print_activation_message(type)

    elif type == CONDA_TYPE:
        if __check_dependencies(CONDA_TYPE):
            __return_command(f"conda activate {environment_file_or_name}")
            __print_activation_message(type)

    else:
        __print_information(
            f"Something went wrong! Do not know environment type '{type}'. "
            "Maybe this was extracted from an file that links this directory?",
        )


if __name__ == "__main__":
    main()
