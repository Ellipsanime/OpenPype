import os
import subprocess
import maya.cmds as cmds
from itertools import cycle

###############################################################################

def get_other_task_folder_path(filepath, tasks=["_shd", "_stp"]):

    # Will store the next task folder path 
    other_task_folder = None

    # Will cycle in the two tasks list
    task_iterator = cycle(tasks)

    # Loop through the given tasks list
    for task in tasks:

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
    
    for maya_file in os.listdir(folder_path):
    
        maya_file_path = os.path.join(folder_path, maya_file).replace("\\","/")
        maya_file_time = os.path.getmtime(maya_file_path)
    
        if newest_file_path is None:
            newest_file_path = maya_file_path
            newest_file_time = maya_file_time
    
        elif maya_file_time > newest_file_time:
            newest_file_path = maya_file_path
            newest_file_time = maya_file_time

    return newest_file_path

###############################################################################

def get_vertice_count():

    # Select all geometries in scene
    geos = cmds.ls(geometry=True)
    cmds.select(geos)

    # Vertice count
    vertice_count = cmds.polyEvaluate(vertex=True)

    return vertice_count

###############################################################################

def get_subprocess_command(maya_scene_path):

    maya_standalone_cmd = (
        'import maya.standalone;'\
        'maya.standalone.initialize("python")'
        )

    command = (
        '{}; import maya.cmds as cmds;'\
        'opened_file = cmds.file(r"{}", open=True);'\
        'geos = cmds.ls(geometry=True);cmds.select(geos);'\
        'vertice_count = cmds.polyEvaluate(vertex=True);'\
        'print(vertice_count)'.format(maya_standalone_cmd, maya_scene_path)
        )

    return command

###############################################################################

def main():

    # Get actual scene file's path
    actual_file_path = cmds.file(query=True, sceneName=True)

    # Check if we are in a correct task
    if not "_shd" in actual_file_path:
        if not "_stp" in actual_file_path:
            print("This check only apply to SHD or STP scene.")
            return

    # Get the path of the file we want to compare to the actual scene
    other_task_folder = get_other_task_folder_path(actual_file_path)
    newest_file_path  = get_newest_file_path(other_task_folder)

    # Get the subprocess command for the other file
    command = get_subprocess_command(newest_file_path)

    # Get the vertice count for both the other scene and the actual one
    other_scene_vertice_count = int(subprocess.check_output(['mayapy', '-c', command]))
    actual_scene_vert_count   = get_vertice_count()

    # Check
    if other_scene_vertice_count == actual_scene_vert_count:
        print("YOUPI :D")

    else:
        print("other scene vertice count : ", other_scene_vertice_count)
        print("actual scene vert count   : ", actual_scene_vert_count)
        print("pas youpi :(")

###############################################################################
