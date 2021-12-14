import sys
import pymel.core as pm

###############################################################################

required_prefixes = ["grp_", "geo_", "msh_", "prx_", "gab_"]

def list_grps_in_outliner():

    top_nodes = pm.ls(assemblies=True)

    outliner_grps = []

    for node in top_nodes:
        if node.getShape():
            continue
        else:
            outliner_grps.append(node)

    return outliner_grps

###############################################################################

def get_geo_grp_members(all_grp_children):

    geo_grp_children = []
    
    for child in all_grp_children:
        if child == "GEO":
            geo_grp_children = child.getChildren()

    return geo_grp_children

###############################################################################

def check(stream=sys.stdout):

    stream.write('running check for ouliner content and hierarchy...\n')

    outliner_grps = list_grps_in_outliner()

    # Check if there is no group in the scene
    if not outliner_grps :
        stream.write("... Outliner doesn't contain any group.\n")
        return False

    # Check if the top group is named "ALL"
    if outliner_grps[0] != "ALL":
        stream.write("... Top group is not named 'ALL'.\n")
        return False

    # Check if "ALL" contains a "GEO" group 
    all_grp_children = outliner_grps[0].getChildren()

    if not "GEO" in all_grp_children:
        stream.write("... 'ALL' group doesn't contain 'GEO' group.\n")
        return False

    # Get the members of "GEO" group
    geo_grp_children = get_geo_grp_members(all_grp_children)

    for item in geo_grp_children:
        if item[:4] not in required_prefixes:
            stream.write("... Naming convention with {}.\n".format(item))
            return False

    return True
