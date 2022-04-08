'''

stub = photoshop.stub()


class CropImage(pyblish.api.ContextPlugin):
    """Crop Image
    ...
    """

    label = "Crop Image"
    hosts = ["photoshop"]
    order = pyblish.api.ValidatorOrder + 0.51

    def process(self, context):
        stub().crop(889, 49, 2951, 2111)
'''
