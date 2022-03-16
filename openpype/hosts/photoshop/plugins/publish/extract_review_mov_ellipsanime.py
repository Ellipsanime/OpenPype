from multiprocessing.sharedctypes import Value
import os
import shutil

import pyblish
import openpype.api
import openpype.lib
from openpype.hosts.photoshop import api as photoshop


class ExtractReviewMovEllipsanime(openpype.api.Extractor):
    """
        Produce a flattened or sequence image file from all 'image' instances.

        If no 'image' instance is created, it produces flattened image from
        all visible layers.
    """

    order = pyblish.api.ExtractorOrder + 0.05
    label = "Extract Review Mov [Ellipsanime]"
    hosts = ["photoshop"]
    families = ["review"]

    # Extract Options
    jpg_options = None
    mov_options = None
    make_image_sequence = None

    def process(self, instance):
        ffmpeg_path = openpype.lib.get_ffmpeg_tool_path("ffmpeg")
        for representation in instance.data["representations"]:
            if "sequence_file" not in representation:
                continue
            staging_dir = representation["stagingDir"]
            img_list = representation["files"]
            fps = representation["fps"]
            mov_path = os.path.join(staging_dir, "review.mov")
            self.log.info(f"Generate mov review: {mov_path}")
            img_number = len(img_list)
            to_clean = []
            for i, img in enumerate(img_list):
                src = os.path.join(staging_dir, img)
                dst = os.path.join(staging_dir, "{:0>4}.jpg".format(i))
                shutil.copy(src, dst)
                to_clean.append(dst)

            args = [
                ffmpeg_path,
                "-y",
                "-i", os.path.join(staging_dir, "%04d.jpg"),
                "-filter:v", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                "-frames:v", str(img_number),
                mov_path
            ]
            output = openpype.lib.run_subprocess(args)
            for each in to_clean:
                os.remove(each)
            self.log.debug(output)
            instance.data["representations"].append({
                "name": "mov",
                "ext": "mov",
                "files": os.path.basename(mov_path),
                "stagingDir": staging_dir,
                "frameStart": 1,
                "frameEnd": img_number,
                "fps": fps,
                "preview": True,
                "tags": "shotgridreview"
            })

            # Required for extract_review plugin (L222 onwards).
            instance.data["frameStart"] = 1
            instance.data["frameEnd"] = img_number
            instance.data["fps"] = 1

            self.log.info(f"Extracted {instance} to {staging_dir}")
