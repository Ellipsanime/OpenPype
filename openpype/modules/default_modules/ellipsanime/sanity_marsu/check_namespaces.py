#-*- coding: utf-8 -*-

__author__ = "Boudjerda Selami"
__maintainer__ = "Boudjerda Selami"
__email__ = "selami.boudjerda@ellipsanime.net"

import sys
import maya.cmds as cmds

BASE_NAMESPACES = ["UI", "shared"]

unwanted_namespaces = []

###############################################################################

def name():
    return 'Unwanted Namespaces'


def check(stream=sys.stdout):
    """ Check if any namespace are found in the saved scene.
    """
    global unwanted_namespaces
    del unwanted_namespaces[:]

    # cmds.namespace(setNamespace=':') # /!\ this may harm the scene!!
    namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)

    for ns in namespaces:
        if ns not in BASE_NAMESPACES:
            unwanted_namespaces.append(ns)

    if unwanted_namespaces:
        for item in unwanted_namespaces:
            stream.write(item)
            stream.write('\n')
        return False

    return True

###############################################################################

if __name__ == "__main__":
    ok = check()
    if not ok:
        print unwanted_namespaces
