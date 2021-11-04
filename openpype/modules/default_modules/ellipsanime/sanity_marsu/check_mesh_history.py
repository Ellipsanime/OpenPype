#-*- coding: utf-8 -*-

__author__     = "Boudjerda Selami"
__maintainer__ = "Boudjerda Selami"
__email__      = "selami.boudjerda@ellipsanime.net"

import sys
import maya.mel as mel 
import maya.cmds as cmds

###########################################################################

# Global
geos_with_history = []

###########################################################################

def get_geos_with_history():

    geos = cmds.ls(geometry=True) # type = ["mesh", "shape"])

    geos_with_history = []

    for element in geos:
        history_list = cmds.listHistory(element)

        if history_list and len(history_list) > 1:
            geos_with_history.append(element)

    return geos_with_history

###########################################################################

def delete_history_in_listed_geos(geos_with_history):

    for geo in geos_with_history:
        mel.eval("DeleteAllHistory")

###########################################################################

def check(stream=sys.stdout):

    global geos_with_history
    geos_with_history = get_geos_with_history()

    if geos_with_history:
        return False
    else:
        return True

###########################################################################

def highlight(stream=sys.stdout):

    if not geos_with_history:
        return

    for geo in geos_with_history:
        cmds.select(geo, add=True)

###########################################################################

def resolve(stream=sys.stdout):

    if not geos_with_history:
        return

    delete_history_in_listed_geos(geos_with_history)

###########################################################################

if __name__ == "__main__":

    check()
    highlight()
    resolve()
