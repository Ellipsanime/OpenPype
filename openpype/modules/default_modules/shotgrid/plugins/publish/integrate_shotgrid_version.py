import os
import pyblish.api


class IntegrateShotgridVersion(pyblish.api.ContextPlugin):
    """ Integrate Shotgrid Version """

    order = pyblish.api.IntegratorOrder+0.497
    label = "Shotgrid Version"

    def process(self, context):

        sg = context.data.get("shotgridSession")

        code = os.path.splitext(os.path.basename(context.data.get("currentFile")))[0]

        version_data = {
            "project": context.data.get("shotgridProject"),
            "code": code,
            "sg_task": context.data.get("shotgridTask"),
            "entity": context.data.get("shotgridEntity")
        }
        print(version_data)
        version = sg.create("Version", version_data)
        context.data["shotgridVersion"] = version

        self.log.info("Created Shotgrid version: {}".format(version))
