import sys
import maya.cmds as cmds

lamina_faces = []

def name():
    return 'Topo: manifold edges'

def check(stream=sys.stdout):

    global lamina_faces

    if not cmds.objExists('|ALL|GEO'):
        # don't fail if GEO doesn't exist (it's the purpose of another check!)
        return True

    # save current selection
    sel = cmds.ls(sl=1)

    # select all under |ALL|GEO
    cmds.select('|ALL|GEO', hierarchy=True)

    # list non manifold edges
    lamina_faces = cmds.polyInfo(laminaFaces=True) or []

    # restore selection
    cmds.select(sel)

    if lamina_faces:
        for issue in lamina_faces:
            stream.write(issue)
            stream.write('\n')
        return False

    return True