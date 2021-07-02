import pyblish.api


class CollectMoreInformation(pyblish.api.InstancePlugin):
    """Collect test information withing test collector"""

    order = pyblish.api.CollectorOrder - 0.5
    label = "Collect more info family"
    families = ["model", "model", "animation", "look", "rig", "camera"]
    hosts = ["maya"]

    def process(self, instance):
        print(type(instance))
