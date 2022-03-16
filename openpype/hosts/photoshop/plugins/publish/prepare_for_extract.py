import re

import pyblish.api
import openpype.api
from openpype.hosts.photoshop import api as photoshop


stub = photoshop.stub()


class PrepareForExtract(pyblish.api.ContextPlugin):
    """Validate sheets set as visible

    ...
    """

    label = "Prepare for extract"
    hosts = ["photoshop"]
    order = pyblish.api.ValidatorOrder + 0.5

    def process(self, context):
        for layer in stub.get_layers_metadata().values():
            self.log.info(layer)
            if "placeholder" in layer["id"]:
                should_be_visible = False
            elif "instance" in layer["id"]:
                should_be_visible = True
            else:
                continue
            stub.set_visible(layer['uuid'], should_be_visible)
