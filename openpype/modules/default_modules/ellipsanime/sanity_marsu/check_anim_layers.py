import sys
import maya.cmds as cmds

unwanted_anim_layers = []

###############################################################################

def name():
    return 'Unwanted Anim Layers'


def check(stream=sys.stdout):
    del unwanted_anim_layers[:]

    unwanted_anim_layers.extend(cmds.ls(type='animLayer') or [])

    if unwanted_anim_layers:
        for item in unwanted_anim_layers:
            stream.write(item)
            stream.write('\n')
        return False

    return True


def highlight():
    if unwanted_anim_layers:
        cmds.select(unwanted_anim_layers)


def resolve():
    if unwanted_anim_layers:
        cmds.delete(unwanted_anim_layers)


###############################################################################

if __name__ == "__main__":
    ok = check()
    if not ok:
        print unwanted_anim_layers
