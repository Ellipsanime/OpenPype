import sys
import maya.cmds as cmds
import maya.mel as mel


ngons = []


def name():
    return 'Topo: n-gons'


def check(stream=sys.stdout):
    global ngons
    if not cmds.objExists('|ALL|GEO'):
        # don't fail if GEO doesn't exist (its the purpose of another check!)
        return True
    # save current selection
    sel = cmds.ls(sl=1)
    # select all under |ALL|GEO
    cmds.select('|ALL|GEO', hierarchy=True)
    # select n-gons
    cmds.polySelectConstraint(mode=3, type=8, size=3) # all / edges / nsided
    # store n-gons in `ngons` global
    ngons = cmds.ls(sl=1) or []
    # restore selection
    cmds.select(sel)
    if ngons:
        for entry in ngons:
            stream.write(entry)
            stream.write('\n')
        return False

    return True
