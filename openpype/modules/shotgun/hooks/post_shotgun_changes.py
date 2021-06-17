import os

from openpype.lib import PostLaunchHook


class PostShotgunHook(PostLaunchHook):
    order = None

    def execute(self, *args, **kwargs):
        print(args, kwargs)
        pass
