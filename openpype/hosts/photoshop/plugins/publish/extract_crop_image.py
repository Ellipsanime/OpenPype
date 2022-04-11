import openpype.api
from openpype.hosts.photoshop import api as photoshop


class CropImage(openpype.api.Extractor):
    """Crop Image before export."""

    order = openpype.api.Extractor.order - 0.491
    label = "Crop Image"
    hosts = ["photoshop"]
    families = ["workfile"]

    def process(self, instance):
        photoshop.stub().crop(889, 49, 2951, 2111)