import sys
import maya.cmds as cmds
import maya.mel as mel

zero_len_edges = []

def name():
    return 'Topo: Zero length edges'

def check(stream=sys.stdout):

    global zero_len_edges

    if not cmds.objExists('|ALL|GEO'):
        # don't fail if GEO doesn't exist (its the purpose of another check!)
        return True

    # save current selection
    sel = cmds.ls(sl=1)

    # select all under |ALL|GEO
    cmds.select('|ALL|GEO', hierarchy=True)

    # select concave/convexe faces
    zero_len_edges = mel.eval('polyCleanupArgList 4 {"1","2","1","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0"};')

    # restore selection
    cmds.select(sel)
    if zero_len_edges:
        for issue in zero_len_edges:
            stream.write(issue)
            stream.write('\n')
        return False

    return True

