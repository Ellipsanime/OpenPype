#-*- coding: utf-8 -*-

__author__ = "Boudjerda Selami"
__maintainer__ = "Boudjerda Selami"
__email__ = "selami.boudjerda@ellipsanime.net"

import sys
import maya.cmds as cmds

###############################################################################

PROD_ROOTS = ('${PROD_ROOT}', '$PROD_ROOT')

type_attr_mode_list = [
                    ('file', 'fileTextureName'),
                    ('audio', 'filename'),
                    ('gpuCache', 'cacheFileName'),
                    # ('substance', 'package'),
                    # ('pgYetiMaya', 'imageSearchPath'),
                    # ('pgYetiMaya', 'outputCacheFileName'),
                    # ('pgYetiMaya', 'cacheFileName'),
                    # ('RedshiftProxyMesh', 'fileName'),
                    # ('pxrUsdReferenceAssembly', 'filePath'),
                    ]

issue_list = []

def name():
    return '${PROD_ROOT} Prefixes'


def check(stream=sys.stdout):
    """ Check that specific "path" attributes have their `${PROD_ROOT}` prefix
    """
    global issue_list
    del issue_list[:]

    for object_type, attribute_name in type_attr_mode_list:
        for o in cmds.ls(type=object_type):
            attr_dagpath = o + '.' + attribute_name
            path = cmds.getAttr(attr_dagpath)
            if path and not path.startswith(PROD_ROOTS):
                issue_list.append(attr_dagpath)

    if issue_list:
        for item in issue_list:
            stream.write(item)
            stream.write('\n')
        return False

    return True


def highlight(stream=sys.stdout):
    cmds.select([ o[:o.rfind('.')] for o in issue_list ])


def resolve(stream=sys.stdout):
    import j_smurfs.utils
    for attr in issue_list:
        path = cmds.getAttr(attr)
        stream.write('prodrootify {}\n'.format(attr))
        cmds.setAttr(attr, j_smurfs.utils.prodrootify(path), type='string')



if __name__ == "__main__":
    ok = check()
    if not ok:
        print issue_list
