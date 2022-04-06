import os
import re
import openpype.api
from openpype.hosts.photoshop import api as photoshop


class ExtractImageEllipsanime(openpype.api.Extractor):
    """Produce a flattened image file from instance

    This plug-in takes into account only the layers in the group.

    Ellipsanime modification. Use instances name as Udim.
    """

    label = "Image [Ellipsanim format]"
    hosts = ["photoshop"]
    families = ["image", "background"]
    formats = ["png", "jpg"]

    def process(self, instance):
        staging_dir = self.staging_dir(instance)
        self.log.info("Outputting image to {}".format(staging_dir))

        # Perform extraction
        stub = photoshop.stub()
        files = {}
        with photoshop.maintained_selection():
            self.log.info("Extracting %s" % str(list(instance)))
            with photoshop.maintained_visibility():
                stub.hide_all_others_layers([instance[0]])

                file_basename = os.path.splitext(
                    stub.get_active_document_name()
                )[0]
                sheet_number = re.search(r'(\d+)$', instance.data["name"])
                sheet_name = re.search(r'[a-zA-Z]+', instance.data["name"]).group()
                if sheet_number:
                    sheet_number = sheet_number.group()
                else:
                    raise ValueError(
                        "Sheet '{}' has invalid name, should end with digits".format(instance.data["name"]))
                padded_sheet_number = "{:0>4}".format(sheet_number)
                file_basename = file_basename + '.{}'.format(
                    padded_sheet_number)
                if '_turnconfo_' in file_basename:
                    splitted_file_basename = file_basename.find('_v')
                    file_basename = file_basename[:splitted_file_basename] + '_{}'.format(sheet_name) + file_basename[splitted_file_basename:]

                for extension in self.formats:
                    _filename = "{}.{}".format(file_basename, extension)
                    files[extension] = _filename

                    full_filename = os.path.join(staging_dir, _filename)
                    stub.saveAs(full_filename, extension, True)
                    self.log.info(f"Extracted: {extension}")

        representations = []
        instance.data['fps'] = padded_sheet_number
        #FIXME: fix using instance.context.data stuff or collector or whatever
        layers_meta = stub.get_layers_metadata()
        layers = [
            stub.get_layer(layer.get('uuid')) for layer in layers_meta.values()
            if layer and "placeholder" not in layer["id"]
        ]
        layers = [layer for layer in layers if layer]
        number_of_images = len(layers)
        for i, (extension, filename) in enumerate(files.items()):

            representations.append({
                "name": extension,
                "ext": extension,
                "files": filename,
                "stagingDir": staging_dir,
                "fps": padded_sheet_number,
                "resolutionWidth": "1080",
                "frameEnd": number_of_images,
                "currentFrame": int(sheet_number),
                "tags": ["burnin"]
            })

        instance.data["representations"] = representations
        instance.data["stagingDir"] = staging_dir

        self.log.info(f"Extracted {instance} to {staging_dir}")
