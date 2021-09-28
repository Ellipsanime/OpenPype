import os
import pyblish.api


class IntegrateShotgridVersion(pyblish.api.ContextPlugin):
    """ Integrate Shotgrid Version """

    order = pyblish.api.IntegratorOrder+0.497
    label = "Shotgrid Version"

    sg = None

    def process(self, context):

        self.sg = context.data.get("shotgridSession")

        code = os.path.splitext(os.path.basename(context.data.get("currentFile")))[0]

        version = self._find_existing_version(code, context)

        if not version:
            version = self._create_version(code, context)
            self.log.info("Create Shotgrid version: {}".format(version))
        else:
            self.log.info("Use existing Shotgrid version: {}".format(version))

        context.data["shotgridVersion"] = version

    def _find_existing_version(self, code, context):

        filters = [
            ["project", "is", context.data.get("shotgridProject")],
            ["sg_task", "is", context.data.get("shotgridTask")],
            ["entity", "is", context.data.get("shotgridEntity")],
            ["code", "is", code]
        ]
        return self.sg.find_one("Version", filters, [])

    def _create_version(self, code, context):

        version_data = {
            "project": context.data.get("shotgridProject"),
            "sg_task": context.data.get("shotgridTask"),
            "entity": context.data.get("shotgridEntity"),
            "code": code,
        }

        version_data = {**version_data, **_additional_version_data(context)}

        return self.sg.create("Version", version_data)


def _additional_version_data(context):
    data = {}

    status = context.data.get("intent", {}).get("value")
    if status:
        data["sg_status_list"] = status

    return data
