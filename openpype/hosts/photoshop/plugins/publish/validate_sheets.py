import collections
from multiprocessing.sharedctypes import Value
import pyblish.api
import openpype.api
from openpype.hosts.photoshop import api as photoshop
import re

stub = photoshop.stub()


class ValidateSheets(pyblish.api.ContextPlugin):
    """
    Why :
        Validate that all sheets are here
    How :
        Validator check each sheets ending number.
        An error is raised if there is a gap.

    How to fix:
        Use studio tools to add sheets until there is no more gap.
        Migrate layers in yours sheets to fill the gap and remove
        unused ones.
    """

    label = "No missing sheet"
    hosts = ["photoshop"]
    order = openpype.api.ValidateContentsOrder

    def process(self, context):
        layer_numbers = []
        for layer in stub.get_layers_metadata().values():
            if "instance" not in layer['id']:
                continue
            match = re.search(r"(\d+)$", layer["subset"])
            assert match, "Layer {} should end with digits".format(
                layer["subset"])
            layer_numbers.append(int(match.group()))

        current_layers = set(layer_numbers)
        normal_layers = set(range(1, max(layer_numbers) + 1))
        missing_layers = normal_layers - current_layers
        assert missing_layers == set(), "Missing layers: {}".format(
            missing_layers)
