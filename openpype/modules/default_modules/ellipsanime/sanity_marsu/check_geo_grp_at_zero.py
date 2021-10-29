#-*- coding: utf-8 -*-

__author__ = "Boudjerda Selami"
__maintainer__ = "Boudjerda Selami"
__email__ = "selami.boudjerda@ellipsanime.net"

import sys
import maya.cmds as cmds

###############################################################################

GROUP_NAMES = ["|ALL", "|ALL|GEO"]
IDENTITY_MATRIX = [ 1.0,0.0,0.0,0.0,
                    0.0,1.0,0.0,0.0,
                    0.0,0.0,1.0,0.0,
                    0.0,0.0,0.0,1.0 ]

groups_not_at_zero = []


def name():
    return "|ALL and |ALL|GEO at zero"


def check(stream=sys.stdout):
    """ Check if the main groups have no transformations.
    """
    global groups_not_at_zero
    del groups_not_at_zero[:]


    # List of the group to check

    # Check position
    for grp in GROUP_NAMES:

        if cmds.objExists(grp):
            mtx = cmds.xform(grp, query=True, matrix=True)
            if mtx != IDENTITY_MATRIX:
                groups_not_at_zero.append(grp)


    if groups_not_at_zero:
        for item in groups_not_at_zero:
            stream.write(item)
            stream.write('\n')
        return False

    return True

###############################################################################

if __name__ == "__main__":
    ok = check()
    if not ok:
        print groups_not_at_zero
