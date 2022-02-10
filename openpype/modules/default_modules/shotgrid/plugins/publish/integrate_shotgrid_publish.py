import os
import pyblish.api

class IntegrateShotgridPublish(pyblish.api.InstancePlugin):
    """
    Create published Files from representations and add it to version. If
    representation is tagged add shotgrid review, it will add it in
    path to movie for a movie file or path to frame for an image sequence.
    """

    order = pyblish.api.IntegratorOrder+0.499
    label = "Shotgrid Published Files"

    def process(self, instance):

        context = instance.context

        self.sg = context.data.get("shotgridSession")

        shotgrid_version = instance.data.get("shotgridVersion")

        for representation in instance.data.get("representations", []):

            local_path = representation.get("published_path")
            code = os.path.basename(local_path)

            if "thumbnail" in representation.get("tags", []):
                continue

            if "shotgridreview" in representation.get("tags", []):
                self.log.info(
                    "Upload review: {} for version shotgrid {}".format(
                        local_path, shotgrid_version.get("id"))
                )
                self.sg.upload(
                    "Version",
                    shotgrid_version.get("id"),
                    local_path,
                    field_name="sg_uploaded_movie"
                )

                data_path_to = {}
                if representation["ext"] in ["mov", "avi"]:
                    data_path_to["sg_path_to_movie"] = local_path
                elif representation["ext"] in ["jpg", "png", "exr", "tga"]:
                        data_path_to["sg_path_to_frames"] = local_path

                self.sg.update(
                    "Version",
                    shotgrid_version.get("id"),
                    data_path_to
                )
                continue

            published_file = self._find_existing_publish(
                code,
                context,
                shotgrid_version
            )

            published_file_data = {
                "project": context.data.get("shotgridProject"),
                "code": code,
                "entity": context.data.get("shotgridEntity"),
                "task": context.data.get("shotgridTask"),
                "version": shotgrid_version,
                "path": {"local_path": local_path}
            }
            if not published_file:
                published_file = self._create_published(published_file_data)
                self.log.info(
                    "Create Shotgrid PublishedFile: {}".format(published_file)
                )
            else:
                self.sg.update(
                    published_file["type"],
                    published_file["id"],
                    published_file_data
                )
                self.log.info(
                    "Update Shotgrid PublishedFile: {}".format(published_file)
                )

            if instance.data["family"] == 'image':
                self.sg.upload_thumbnail(
                    published_file["type"],
                    published_file["id"],
                    local_path
                )

            instance.data["shotgridPublishedFile"] = published_file

    def _find_existing_publish(self, code, context, shotgrid_version):

        filters = [
            ["project", "is", context.data.get("shotgridProject")],
            ["task", "is", context.data.get("shotgridTask")],
            ["entity", "is", context.data.get("shotgridEntity")],
            ["version", "is", shotgrid_version],
            ["code", "is", code],
        ]
        return self.sg.find_one("PublishedFile", filters, [])

    def _create_published(self, published_file_data):

        return self.sg.create("PublishedFile", published_file_data)
