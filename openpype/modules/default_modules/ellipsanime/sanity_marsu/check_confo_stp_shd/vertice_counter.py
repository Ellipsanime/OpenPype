#-*- coding: utf-8 -*-

__author__      = "Boudjerda Selami"
__maintainer__  = "Boudjerda Selami"
__email__       = "selami.boudjerda@ellipsanime.net"

import maya.cmds as cmds

###############################################################################
#                                                                             #
###############################################################################

def get_vertice_count():

    vertice_count_by_meshes = {}

    # Select all geometries in scene
    geos = cmds.ls(geometry=True)

    for geo in geos:
        cmds.select(geo)
        vertice_count = cmds.polyEvaluate(vertex=True)

        # Sometime, selected element are not geo (ex: ctrl)
        if isinstance(vertice_count, unicode):
            continue
        else:
            vertice_count_by_meshes[geo] = vertice_count

    return vertice_count_by_meshes

###############################################################################

def compare(local_count, other_task_count):

    is_conform = True

    print
    print(" .................................. comparing vertiice count")

    for geo_name, vertice_count in local_count.iteritems():

        if geo_name not in other_task_count:
            continue

        else:
            if vertice_count == other_task_count[geo_name]:
                continue

            elif vertice_count != other_task_count[geo_name]:
                print("DIFFERENCE DE NOMBRE DE VERTEX : ")
                print("    \____ {} local  = {}".format(geo_name, vertice_count))
                print("     \___ {} extern = {}".format(geo_name, other_task_count[geo_name]))
                is_conform = False

    # Conclusion print if everything is ok
    if is_conform:
        print("    \____ Nombre de vertice conforme")

    return is_conform

###############################################################################

def main():
    print({"vertice_counter" : get_vertice_count()})
    return get_vertice_count()
