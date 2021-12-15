import os
import pyblish.api
import pprint


class IntegrateShotgridPublish(pyblish.api.InstancePlugin):
    """ Commit components to server. """

    order = pyblish.api.IntegratorOrder+0.499
    label = "Shotgrid Published Files"

    def process(self, instance):

        context = instance.context
        sg = context.data.get("shotgridSession")

        subset_id = context.data.get("subsetEntity", {}).get("_id")

        version_id = context.data.get("versionEntity", {}).get("_id")

        shotgrid_version = instance.data.get("shotgridVersion")

        for representation in instance.data.get("representations", []):

            local_path = representation.get("published_path")

            code = os.path.basename(local_path)

            published_file_data = {
                "project": context.data.get("shotgridProject"),
                "code": code,
                "entity": context.data.get("shotgridEntity"),
                "task": context.data.get("shotgridTask"),
                "version": shotgrid_version,
                "path": {"local_path": local_path}
            }

            sg_pub_file = sg.create("PublishedFile", published_file_data)

            if "shotgridreview" in representation.get("tags", []):
                self.log.info("Upload review: {} for version shotgrid {}".format(local_path, shotgrid_version.get("id")))
                sg.upload("Version", shotgrid_version.get("id"), local_path, field_name="sg_uploaded_movie")

            instance.data["shotgridPublishedFile"] = sg_pub_file
            self.log.info("Created Shotgrid PublishedFile: {}".format(sg_pub_file))
