from openpype.modules.default_modules.shotgrid.lib import settings, server


class ManagerApi():

    def getProjectList(self):
        print("get project list")
        return settings.get_project_list()

    def getProjectBatchInfos(self, project):
        print('get project batch info for project ', project)
        s = settings.get_shotgrid_project_settings(project)
        auth = s.get('auth', {})
        response = {
            'url': auth.get("project_shotgrid_url", ""),
            'script_name': auth.get("project_shotgrid_script_name", ""),
            'api_key': auth.get("project_shotgrid_script_key", ""),
            'project_id': s.get("shotgrid_project_id", None),
            'fields_mapping': s.get("fields", {})
        }
        return response

    def checkProjectSettings(self, settings):
        print('Check project ', settings)
        op_settings = {
            'auth': {
                'project_shotgrid_url': settings['url'],
                'project_shotgrid_script_name': settings['script_name'],
                'project_shotgrid_script_key': settings['api_key'],
            },
            'shotgrid_project_id': settings['project_id']
        }
        if not server.check_batch_settings(settings['project'], op_settings):
            return False
        return True
