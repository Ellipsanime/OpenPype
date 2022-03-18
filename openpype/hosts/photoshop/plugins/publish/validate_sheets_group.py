from logging import warning
from multiprocessing.sharedctypes import Value
import pyblish.api
import openpype.api
from openpype.hosts.photoshop import api as photoshop

stub = photoshop.stub()


class ValidateSheetsGroup(pyblish.api.ContextPlugin):
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

    label = "No renamed sheet"
    hosts = ["photoshop"]
    order = openpype.api.ValidateContentsOrder
    block_pipe = True

    def process(self, context):
        renamed_groups = []
        for layer in stub.get_layers_metadata().values():
            if "instance" not in layer['id']:
                continue
            sheet_name = layer["subset"]
            layer_group = stub.get_layer(layer['uuid'])
            group_name = layer_group.name[2:]
            if group_name != sheet_name:
                renamed_groups.append((group_name, sheet_name))

        renamed_groups_errors = [
            f"Layer group {bad_result[1]} as been renamed in {bad_result[0]}, this should not happen."
            for bad_result in renamed_groups
        ]
        if renamed_groups_errors:
            if self.block_pipe:
                assert not renamed_groups_errors, renamed_groups_errors
            self.log.warning(renamed_groups_errors)
