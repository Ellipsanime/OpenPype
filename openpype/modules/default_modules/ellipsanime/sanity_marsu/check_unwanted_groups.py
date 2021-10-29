#-*- coding: utf-8 -*-

__author__ = "Boudjerda Selami"
__maintainer__ = "Boudjerda Selami"
__email__ = "selami.boudjerda@ellipsanime.net"

import sys
import maya.cmds as cmds

###############################################################################

# List of unwanted node in the outliner
unwanted_groups = []


def name():
    return 'Unwanted Groups'


def check(stream=sys.stdout):
    """ Check for unwanted groups at the top of the DAG hierarchy.
        Basically, the goal is to keep the "|ALL" group only.
    """
    global unwanted_groups
    del unwanted_groups[:]

    # List top nodes in outliner
    top_nodes = cmds.ls(assemblies=True, long=True)

    # Loop though the outliner node list
    for top_node in top_nodes:
        children = cmds.listRelatives(top_node, children=True, fullPath=True)

        # If the 1st child of the looped node is not a transform, don't process.
        # It might be cameras or lights etc. We just want to get unwanted groups.
        if children and cmds.objectType(children[0]) != 'transform':
            continue

        # Else, if it's not the wanted node name, list it
        elif top_node != '|ALL':
            unwanted_groups.append(top_node)

    if unwanted_groups:
        for item in unwanted_groups:
            stream.write(item)
            stream.write('\n')
        return False

    return True

###############################################################################

if __name__ == "__main__":
    ok = check()
    if not ok:
        for node in unwanted_groups:
            print node
