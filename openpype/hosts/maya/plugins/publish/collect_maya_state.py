import maya.cmds as cmds
import pyblish.api


class CollectMayaState(pyblish.api.ContextPlugin):
    """Collect Maya's scene units."""

    label = "Maya Units"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]

    def process(self, context):

        # Get the current linear units
        context.data['mayaStateIsBatch'] = cmds.about(query=True, batch=True)
