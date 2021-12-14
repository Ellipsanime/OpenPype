import sys
import maya.cmds as cmds


IDENTITY = [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]


unwanted_transforms = []

def name():
    return 'Stray Transform Values'


def check(stream=sys.stdout):

    del unwanted_transforms[:]

    xforms = cmds.ls('|ALL|GEO', dagObjects=True, type='transform') or []
    xforms.append('ALL')

    for o in xforms:
        m = cmds.getAttr(o + '.matrix')
        if m != IDENTITY:
            unwanted_transforms.append(o)

    if unwanted_transforms:
        for item in unwanted_transforms:
            stream.write(item)
            stream.write('\n')
        return False

    return True

