#-*- coding: utf-8 -*-

__author__      = "Boudjerda Selami"
__maintainer__  = "Boudjerda Selami"
__email__       = "selami.boudjerda@ellipsanime.net"

import maya.cmds as cmds

"""
Create a dictionary from the outliner groups hierarchy.
"""

###############################################################################
#                                                                             #
###############################################################################

def get_topnode():

    assemblies_list = cmds.ls(assemblies=True)
    to_exclude_list = ['persp', 'top', 'front', 'side']

    for asm in assemblies_list:
        if asm not in to_exclude_list:
            topnode = asm
        else:
            topnode = None

    return topnode

###############################################################################

def get_hierarchy_tree(parent_node, tree):

    childrens = cmds.listRelatives(
            parent_node, children=True, type='transform', fullPath=True)

    if childrens:
        tree[parent_node] = {}
        for child in childrens:
            get_hierarchy_tree(child, tree[parent_node])

###############################################################################

def format_hierarchy_tree(tree, hierarchy_members=[]):

    hierarchy_list = hierarchy_members

    for parent_grp, children_grp in tree.iteritems():
        if parent_grp not in hierarchy_list:
            hierarchy_list.append(parent_grp)
        format_hierarchy_tree(children_grp, hierarchy_list)

    return hierarchy_list

###############################################################################

def compare(local_hierarchy, other_task_hierarchy):

    is_conform = True

    print
    print(" .................................. comparing hierarchy")

    # List may have different size. We just want to check what is not conform.
    # Compare local hierarchy to the other task hierarchy
    for local_element in local_hierarchy:
        if local_element not in other_task_hierarchy:
            print("    \____ Cet element est manquant dans la hierarchies LOCALE: {}".format(local_element))
            is_conform = False

    # Compare the other task hierarchy to local hierarchy
    for other_element in other_task_hierarchy:
        if other_element not in local_hierarchy:
            print("    \____ Cet element est manquant dans la hierarchies EXTERNE: {}".format(other_element))
            is_conform = False

    # Conclusion print if everything is ok
    if is_conform:
        print("    \____ Hierarchie conforme")

    return is_conform

###############################################################################

def main():

    result = {}

    top_node = "ALL|GEO" #get_topnode()

    if top_node:
        scene_hierarchy = {}
        get_hierarchy_tree(top_node, scene_hierarchy)

        result = {"hierarchy_getter": format_hierarchy_tree(scene_hierarchy)}

        print(result)
        return result["hierarchy_getter"]

    else:
        cmds.warning("Is your scene empty ? Check the outliner")
        return None

###########################################################################
#                                                                         #
###########################################################################

if __name__ == "__main__":

    hierarchy = main()

    for element in hierarchy:
        print(element)
