# -*- coding: utf-8 -*-
"""Change Reference in local scene object by importing them."""
# import os

# import avalon.maya
import openpype.api


class MakeReferenceLocal(openpype.api.Extractor):
    """Change Reference in local scene object by importing them."""

    label = "Make Reference local"
    hosts = ["maya"]
    families = ["model"]
    scene_type = "ma"
    optional = True
    order = 1.99

    def process(self, instance):
        import pymel.core as pm

        list_references = set()
        for obj_long_name in instance[:]:
            node = pm.PyNode(obj_long_name)

            if not node.isReferenced():
                continue

            list_references.add(node.referenceFile())

        for ref_node in list_references:
            if ref_node.isLoaded():
                ref_node.importContents(removeNamespace=True)

        instance_name = instance.data("name")
        new_members = pm.PyNode(instance_name).members()
        instance.data["setMembers"] = [i.longName() for i in new_members]

        new_children = []
        for member in new_members:
            new_children.extend(member.getChildren(allDescendents=True))

        instance[:] = list(set([i.longName() for i in new_members + new_children]))
