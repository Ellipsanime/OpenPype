import sys
import maya.cmds as cmds

non_manifold_edges = []

def name():
    return 'Topo: manifold edges'

def check(stream=sys.stdout):

    global non_manifold_edges

    if not cmds.objExists('|ALL|GEO'):
        # don't fail if GEO doesn't exist (it's the purpose of another check!)
        return True

    # save current selection
    sel = cmds.ls(sl=1)

    # select all under |ALL|GEO
    cmds.select('|ALL|GEO', hierarchy=True)

    # list non manifold edges
    non_manifold_edges = cmds.polyInfo(nonManifoldEdges=True) or []

    # restore selection
    cmds.select(sel)

    if non_manifold_edges:
        for issue in non_manifold_edges:
            stream.write(issue)
            stream.write('\n')
        return False

    return True
