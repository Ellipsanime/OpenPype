import pyblish.api
import pprint


class IntegrateShotgridPublish(pyblish.api.InstancePlugin):
    """ Commit components to server. """

    order = pyblish.api.IntegratorOrder+0.499
    label = "Integrate Shotgrid Publish"

    def process(self, instance):
        pass
        with open(r"C:\Users\NAZEPC\PycharmProjects\OpenPype\openpype\modules\default_modules\shotgrid\yourlogfile.log", "w") as log_file:
            pprint.pprint(instance.data, log_file)
