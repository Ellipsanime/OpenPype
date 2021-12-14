#-*- coding: utf-8 -*-

__author__      = "Boudjerda Selami"
__maintainer__  = "Boudjerda Selami"
__email__       = "selami.boudjerda@ellipsanime.net"

import os
import sys
import ast
import importlib
import subprocess
from itertools import cycle

import maya.cmds as cmds

missing_in_hierarchy = []  #  <---------------------------------------------- @

###############################################################################
# other task file getter                                                      #
###############################################################################

def get_other_task_folder_path(filepath, tasks=["_shd", "_stp"]):

    # Will store the next task folder path 
    other_task_folder = None

    # Will cycle in the two tasks list
    task_iterator = cycle(tasks)

    # Loop through the given tasks list
    for task in task_iterator:

        # If the looped task is not find in the actual scene path:
        if not task in filepath:
            # Get the ACTUAL task (the next one in the task list)
            actual_task = task_iterator.next()
            # Generate a file path in the looped task
            other_task_path = filepath.replace(actual_task, task)
            # And just keep the folder
            other_task_folder = os.path.dirname(other_task_path)
            break

        else:
            continue

    return other_task_folder

###############################################################################

def get_newest_file_path(folder_path):

    newest_file_time = None
    newest_file_path = None

    for file_name in os.listdir(folder_path):
    
        path = os.path.join(folder_path, file_name)

        # skip directories
        if os.path.isdir(path):
            continue

        # skip non maya .ma files
        if not path.endswith(".ma"):
            continue

        file_name_path = os.path.join(folder_path, file_name).replace("\\","/")
        file_name_time = os.path.getmtime(file_name_path)

        if newest_file_path is None:
            newest_file_path = file_name_path
            newest_file_time = file_name_time

        elif file_name_time > newest_file_time:
            newest_file_path = file_name_path
            newest_file_time = file_name_time

    return newest_file_path

###############################################################################
# mayapy multiscript cmd generator                                            #
###############################################################################

def get_subprocess_command(scripts, maya_scene_path=None):

    if maya_scene_path is None:
        print("Veuillez charger un asset.")
        return

    imports_cmd = (
        'import sys; '\
        'import importlib; '\
        )

    maya_specific_cmd = (
        'import maya.cmds as cmds; '\
        'import maya.standalone; '\
        'maya.standalone.initialize("python"); '\
        'cmds.file(r"{}", open=True); '.format(maya_scene_path)\
        )

    operations_cmd = (
        'scripts_import=[importlib.import_module(i) for i in {0}]; '\
        'scripts_execut=[script.main() for script in scripts_import]'.format(scripts)
        )

    command = "{}{}{}".format(imports_cmd, maya_specific_cmd, operations_cmd)

    return command

###############################################################################

def normalize_subprocess_return(subprocess_return):

    mayapy_result = []

    for line in subprocess_return.stdout:
        if not line.startswith("{"):
            continue
        elif line.startswith("'Hierarchy ': ['ALL|GEO', "):
            for element in line.strip().strip("][").split(", u"):
                mayapy_result.append(element.replace("'", ""))

    return mayapy_result

###############################################################################
# check stp vs shd check launcher                                             #
###############################################################################

def gather_subprocess_result(subproc_result):

    result = {}

    for line in subproc_result.stdout:
        if not line.startswith("{"):
            continue

        result.update(ast.literal_eval(line))

    return result

###############################################################################

def import_modules(scripts):

    # Folder to import from:
    import_folder = "j_smurfs.sanity.check_confo_stp_shd"

    imported_modules = []

    # Import modules contained in scripts list
    for script in scripts:
        module = importlib.import_module("{}.{}".format(import_folder, script))
        #reload(module)
        imported_modules.append(module.__name__)

    return imported_modules

###############################################################################

def launch_external_check(imported_modules, local_data={}, external_data={}, function_name="main"):

    # Return can be a bool or a dict
    if function_name == "main":
        result = {}
    else:
        result = True

    for str_imported_module in imported_modules:

        module = importlib.import_module(str_imported_module)

        # Check if the given scripts contains needed 'main' function to execute
        if not function_name in dir(module):
            print("{} has no '{}' function".format(module, function_name))
            is_conform = False
            continue

        # Empty local_data means we have to work with the external "main" def
        if not local_data:

            # Store the result of the lauched function
            main_function = getattr(module, function_name)
            result[module.__name__] = main_function()

        # Else, we check the name of the function to work with
        elif function_name=="compare":

            # Reduce imported module's longname to its def name
            module_result = module.__name__.rsplit(".", 1)[-1]

            # Proceed
            compare_function = getattr(module, function_name)
            result = compare_function(local_data[module.__name__],
                                    external_data[module_result])

    return result

###############################################################################

def print_datas(scene_data, data_title="LOCAL DATA"):

    print("")
    print(data_title)

    for check_name, listed_values in scene_data.iteritems():
        print(check_name)
        if isinstance(listed_values, dict):
            for key, value in listed_values.iteritems():
                print("   \___ ", key, " : ", value)
        else:
            for value in listed_values:
                print("   \___ ", value)

    print("")
    print("#"*80)

###############################################################################
# CHECKER (main)                                                              #
###############################################################################

def check(stream=sys.stdout):

    scripts = ["hierarchy_getter", "vertice_counter"]

    is_conform = True

    # Import modules from the "scripts" list given as argument
    imported_modules = import_modules(scripts)

    # Get actual scene file's path
    actual_file_path = cmds.file(query=True, sceneName=True)

    # Check if we are in a correct task  TODO @selami : peut être transmis en arg ?
    if not "_shd" in actual_file_path:
        if not "_stp" in actual_file_path:
            print("This check only apply to SHD or STP scene.")
            return False

    # Get the path of the file we want to compare to the actual scene
    other_task_folder = get_other_task_folder_path(actual_file_path)
    newest_file_path  = get_newest_file_path(other_task_folder)

    # If the file does not exist, there's nothing to compare. Abort.
    if not newest_file_path:
        print("Le fichier de l'autre task n'existe pas ou n'est pas publie")
        return False

    # Get the shell command for the subprocess
    cmd = get_subprocess_command(imported_modules, newest_file_path)

    # Execute the shell command
    mayapy_proc = subprocess.Popen(['mayapy', '-c', cmd], stdout=subprocess.PIPE)

    # Get the various data from the other scene and those from the actual scene
    external_data = gather_subprocess_result(mayapy_proc)
    local_data    = launch_external_check(imported_modules)

    # Compare data from both scene
    check_confo = launch_external_check(imported_modules, local_data, external_data, "compare")

    if not check_confo:
        is_conform = False

    # def higlight(list_missing):
    #   selec_les_grp_en_trop?

    return is_conform

###############################################################################
#                                                                             #
###############################################################################

if __name__ == "__main__":

    print(check())
