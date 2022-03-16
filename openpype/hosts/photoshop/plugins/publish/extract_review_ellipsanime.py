from multiprocessing.sharedctypes import Value
import os
import shutil

import openpype.api
import openpype.lib
from openpype.hosts.photoshop import api as photoshop


class ExtractReviewEllipsanime(openpype.api.Extractor):
    """
        Produce a flattened or sequence image file from all 'image' instances.

        If no 'image' instance is created, it produces flattened image from
        all visible layers.
    """

    label = "Extract Review [Ellipsanime]"
    hosts = ["photoshop"]
    families = ["review"]

    # Extract Options
    jpg_options = None
    make_image_sequence = None

    def process(self, instance):
        staging_dir = self.staging_dir(instance)
        self.log.info("Outputting image to {}".format(staging_dir))

        fps = 1
        stub = photoshop.stub()
        self.output_seq_filename = os.path.splitext(
            stub.get_active_document_name())[0] + ".%04d.jpg"

        layers = self._get_layers_from_image_instances(instance)
        if not layers:
            raise ValueError('No layer found, use add sheet in studio tools to start working')
        self.log.info("Layers image instance found: {}".format(layers))
        self.log.info("Extract layers to image sequence.")

        img_list = self._saves_sequences_layers(staging_dir, layers)

        instance.data["representations"].append({
            "name": "jpg",
            "ext": "jpg",
            "files": img_list,
            "sequence_file": img_list[0],
            "frameStart": 0,
            "frameEnd": len(img_list),
            "fps": fps,
            "stagingDir": staging_dir,
            "tags": ["shotgridreview", "burnin"]
        })

        instance.data["stagingDir"] = staging_dir

    def _get_layers_from_image_instances(self, instance):
        stub = photoshop.stub()
        layers_meta = stub.get_layers_metadata()
        layers = [
            stub.get_layer(layer.get('uuid')) for layer in layers_meta.values()
            if layer and "placeholder" not in layer["id"]
        ]

        return sorted(
            (layer for layer in layers if layer),
            key=lambda layer: layer.name
        )

    def _saves_sequences_layers(self, staging_dir, layers):
        import re
        stub = photoshop.stub()

        list_img_filename = []
        with photoshop.maintained_visibility():

            for layer in layers:
                sheet_number = re.search(r'(\d+)$', layer.name)
                if sheet_number:
                    sheet_number = int(sheet_number.group())
                else:
                    raise ValueError(
                        "Sheet '{}' has invalid name, should end with digits".format(layer.name))
                self.log.info("Extracting {}".format(layer.name))
                img_filename = self.output_seq_filename % sheet_number
                output_image_path = os.path.join(staging_dir, img_filename)
                list_img_filename.append(img_filename)
                self.log.info("Output {}".format(output_image_path))
                with photoshop.maintained_visibility():
                    stub.hide_all_others_layers([layer])
                    stub.saveAs(output_image_path, 'jpg', True)

        return list_img_filename
