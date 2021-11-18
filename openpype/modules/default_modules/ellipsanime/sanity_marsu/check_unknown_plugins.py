#-*- coding: utf-8 -*-

__author__ = "Boudjerda Selami"
__maintainer__ = "Boudjerda Selami"
__email__ = "selami.boudjerda@ellipsanime.net"

import sys
import maya.cmds as cmds


unknown_plugins = []

def name():
    return 'Unknown Plugins'


def check(stream=sys.stdout):
    """ Check if some "unknown plugins" are not lying around in the scene
    """
    global unknown_plugins
    unknown_plugins = cmds.unknownPlugin(query=True, list=True)

    if unknown_plugins:
        for item in unknown_plugins:
            stream.write(item)
            stream.write('\n')
        return False

    return True


def resolve(stream=sys.stdout):
    if unknown_plugins:
        for plugin in unknown_plugins:
            stream.write('unload {}...\n'.format(plugin))
            try:
                cmds.unknownPlugin(plugin, remove=True)
            except Exception as err:
                print err


if __name__ == "__main__":
    ok = check()
    if not ok:
        print unknown_plugins
