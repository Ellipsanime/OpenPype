import sys
import maya.cmds as cmds


animated_nodes = []

def name():
    return 'Stray Keys'


def check(stream=sys.stdout):
    del animated_nodes[:]

    time_curves = cmds.ls(type=['animCurveTU', 'animCurveTT', 'animCurveTL', 'animCurveTA'])
    if time_curves:
        connections = cmds.listConnections(time_curves, source=False, destination=True)
        if connections:
            animated_nodes[:] = list(set(connections))
            if animated_nodes:
                for item in animated_nodes:
                    stream.write(item)
                    stream.write('\n')
                return False

    return True