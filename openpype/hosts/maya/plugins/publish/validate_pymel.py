import pyblish.api
import openpype.api


class ValidatePyMel(pyblish.api.ContextPlugin):
    """Validates Pymel is loaded.

    """

    order = openpype.api.ValidateContentsOrder
    families = []
    hosts = ['maya']
    label = 'PyMel is loaded'

    def process(self, instance):
        """Process all the nodes in the instance"""

        loaded = True
        try:
            import pymel.core
        except ModuleNotFoundError:
            loaded = False

        if not loaded:
            raise RuntimeError("PyMel is not loaded, please fix it!")
