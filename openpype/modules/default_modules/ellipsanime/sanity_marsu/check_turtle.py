import sys
import maya.cmds as cmds

def check(stream=sys.stdout):
    loaded_plugins = cmds.pluginInfo(query=True, listPlugins=True)

    stream.write('running check for Turtle plugin...\n')

    for plug in loaded_plugins:
        if plug == "Turtle":
            stream.write('Turtle plugin is loaded...\n')
            return False
        else:
            continue

    return True
