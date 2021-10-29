import sys
import maya.cmds as cmds

unprepared_meshes = []


def name():
    return 'Pre-blendshape setup'


def check(stream=sys.stdout):
    global unprepared_meshes

    del unprepared_meshes[:]

    unprepared_meshes = []
    for msh in cmds.ls('|ALL|GEO', dagObjects=True, type='mesh', noIntermediate=True):
        blendshapes = cmds.listConnections(msh, source=True, destination=False, type='blendShape')
        if not blendshapes:
            unprepared_meshes.append(msh)

    if unprepared_meshes:
        for item in unprepared_meshes:
            stream.write(item)
            stream.write('\n')
        return False

    return True


def highlight(stream=sys.stdout):
    if unprepared_meshes:
        unprepared_xforms = cmds.listRelatives(unprepared_meshes, allParents=True)
        cmds.select(unprepared_xforms)


def resolve(stream=sys.stdout):
    if unprepared_meshes:
        try:
            import j_smurfs.shading.tools
        except:
            import traceback
            traceback.print_exc()
            return

        for o in unprepared_meshes:
            stream.write('setup blendshape on {} ...\n'.format(o))
            j_smurfs.shading.tools.setup_blendshape(o)

