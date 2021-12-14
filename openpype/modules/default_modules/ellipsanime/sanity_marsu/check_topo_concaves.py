import sys
import maya.cmds as cmds

concave_faces = []

def name():
    return 'Topo: concave faces'

def check(stream=sys.stdout):

    global concave_faces

    if not cmds.objExists('|ALL|GEO'):
        # don't fail if GEO doesn't exist (its the purpose of another check!)
        return True

    # save current selection
    sel = cmds.ls(sl=1)

    # select all under |ALL|GEO
    cmds.select('|ALL|GEO', hierarchy=True)

    # select concave/convexe faces
    cmds.polySelectConstraint(mode=3, type=8, convexity=2 )  # get convex faces

    # store concave/convexe faces in `concave_faces` global
    concave_faces = cmds.ls(sl=1) or []

    # restore selection
    cmds.select(sel)
    if concave_faces:
        for issue in concave_faces:
            stream.write(issue)
            stream.write('\n')
        return False

    return True
