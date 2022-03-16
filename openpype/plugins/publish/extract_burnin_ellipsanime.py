import os
import re
import json
import copy
import tempfile
import platform
import shutil

import clique
import six
import pyblish
from openpype.scripts.otio_burnin import burnins_from_data, ModifiedBurnins
import openpype
import openpype.api
from openpype.lib import (
    run_openpype_process,

    get_transcode_temp_directory,
    convert_for_ffmpeg,
    should_convert_for_ffmpeg,

    CREATE_NO_WINDOW
)

SCRIPT_PATH = os.path.normpath(
            os.path.join(openpype.PACKAGE_DIR, "scripts", "otio_burnin.py")
        )



class ExtractBurninEllipsanime(openpype.api.Extractor):
    """
    Extractor to create video with pre-defined burnins from
    existing extracted video representation.

    It will work only on represenations having `burnin = True` or
    `tags` including `burnin`
    """

    label = "Extract burnins [Ellipsanime]"
    order = pyblish.api.ExtractorOrder + 0.03
    families = ["review", "burnin", "image"]
    hosts = ["photoshop"]
    optional = True

    positions = [
        "top_left", "top_centered", "top_right",
        "bottom_right", "bottom_centered", "bottom_left"
    ]
    # Default options for burnins for cases that are not set in presets.
    default_options = {
        "font_size": 42,
        "font_color": [255, 255, 255, 255],
        "bg_color": [0, 0, 0, 127],
        "bg_padding": 5,
        "x_offset": 5,
        "y_offset": 5
    }

    # Preset attributes
    profiles = {
        'families': ['review'], 'hosts': ['photoshop'],

        '__value__': [True, False, True]
    }
    options = {
        'font_size': 42,
        'font_color': '#FFFFFF',
        'bg_color': '#000000',
        'bg_padding': 5,
        'x_offset': 5,
        'y_offset': 5,
        'bg_opacity': 0.4980392156862745,
        'opacity': 1.0,
        'font': 'C:\\Users\\benoit.connan\\Documents\\__GIT\\OpenPype\\openpype\\resources\\fonts\\LiberationSans\\LiberationSans-Regular.ttf'}

    def process(self, instance):
        self.main_process(instance)

        delete_tags = {'delete', 'burnin'}
        for repre in instance.data["representations"]:
            if delete_tags & set(repre.get("tags", [])) == delete_tags:
                self.log.debug("Removing representation: {}".format(repre))
                instance.data["representations"].remove(repre)

    def _get_burnins_per_representations(self, instance, src_burnin_defs):
        self.log.debug("Filtering of representations and their burnins starts")

        filtered_repres = []
        repres = instance.data.get("representations") or []
        for idx, repre in enumerate(repres):
            self.log.debug("repre ({}): `{}`".format(idx + 1, repre["name"]))
            if not self.repres_is_valid(repre):
                continue

            repre_burnin_links = repre.get("burnins", [])
            self.log.debug(
                "repre_burnin_links: {}".format(repre_burnin_links)
            )

            burnin_defs = copy.deepcopy(src_burnin_defs)
            self.log.debug(
                "burnin_defs.keys(): {}".format(burnin_defs.keys())
            )

            # Filter output definition by `burnin` represetation key
            repre_linked_burnins = {
                name: output
                for name, output in burnin_defs.items()
                if name in repre_burnin_links
            }
            self.log.debug(
                "repre_linked_burnins: {}".format(repre_linked_burnins)
            )

            # if any match then replace burnin defs and follow tag filtering
            if repre_linked_burnins:
                burnin_defs = repre_linked_burnins

            # Filter output definition by representation tags (optional)
            repre_burnin_defs = self.filter_burnins_by_tags(
                burnin_defs, repre["tags"]
            )
            if not repre_burnin_defs:
                self.log.info((
                    "Skipped representation. All burnin definitions from"
                    " selected profile does not match to representation's"
                    " tags. \"{}\""
                ).format(str(repre["tags"])))
                continue
            filtered_repres.append((repre, repre_burnin_defs))

        return filtered_repres

    def main_process(self, instance):

        # burnin_defs = self.profiles
        # self.log.debug(burnin_defs)
        # preset = {
        #     'options': self.options,
        #     'burnins': {
        #         'burnin': {
        #             'TOP_LEFT': '{yy}-{mm}-{dd}',
        #             'TOP_CENTERED': '',
        #             'TOP_RIGHT': '{version}',
        #             'BOTTOM_LEFT': '{username}',
        #             'BOTTOM_CENTERED': '{asset}-{task}',
        #             'BOTTOM_RIGHT': '{current_frame}-{frame_end}',
        #             'filter': {
        #                 'families': [],
        #                 'tags': ['shotgridreview']
        #             }
        #         }
        #     }
        # }

        # data = {
        #     "version": 1,
        #     "username": "benoit.connan",
        #     "asset": "asset",
        #     "task": "task",
        #     "current_frame": 1,
        #     "frame_end": 10
        # }
        # Prepare basic data for processing
        # _burnin_data, _temp_data = self.prepare_basic_data(instance)
        # anatomy = instance.context.data["anatomy"]


        # self.log.debug("scriptpath: {}".format(SCRIPT_PATH))

        # # Args that will execute the script
        # executable_args = ["run", SCRIPT_PATH]
        # burnins_per_repres = self._get_burnins_per_representations(
        #     instance, burnin_defs
        # )

        anatomy_data = instance.data.get("anatomyData", {})

        asset = anatomy_data.get("asset")
        task = anatomy_data.get("task", {}).get("name")
        asset_and_task = "{}-{}".format(asset, task)
        username = anatomy_data.get("username")
        day = anatomy_data.get("dd")
        month = anatomy_data.get("mm")
        year = anatomy_data.get("yyyy")
        date = "{}-{}-{}".format(day, month, year)
        version = "v{:0>3}".format(instance.data.get("version", 0))
        is_image = instance.data["family"] == "image"
        representations = instance.data.get("representations", [])
        for repre in representations:
            if not repre["ext"] == "jpg":
                continue
            if "burnin" not in repre["tags"]:
                continue
            repre["tags"].remove("burnin")
            last_frame = repre["frameEnd"]

            options_init = {
                'opacity': 1,
                'x_offset': 10,
                'y_offset': 10,
                'bg_padding': 10,
                'bg_opacity': 0.5,
                'font_size': 52
            }

            def burnin(file, current_frame):
                fullpath = os.path.join(repre["stagingDir"], file)
                # burnins_from_data(each, each)
                # Options init sets burnin look
                burnin = ModifiedBurnins(fullpath, options_init=options_init)
                burnin.add_text(date, ModifiedBurnins.TOP_LEFT)
                burnin.add_text(version, ModifiedBurnins.TOP_RIGHT)
                burnin.add_text(username, ModifiedBurnins.BOTTOM_LEFT)
                burnin.add_text(asset_and_task, ModifiedBurnins.BOTTOM_CENTERED)
                burnin.add_text(
                    "{}/{}".format(current_frame, last_frame),
                    ModifiedBurnins.BOTTOM_RIGHT)
                # Start render (overwrite output file if exist)
                burnin.render(fullpath, overwrite=True)
            if is_image:
                burnin(repre["files"], repre["currentFrame"])
            else:
                for i, file in enumerate(repre["files"]):
                    burnin(file, i + 1)

        #         'burnin': {
        #             'TOP_LEFT': '{yy}-{mm}-{dd}',
        #             'TOP_CENTERED': '',
        #             'TOP_RIGHT': '{version}',
        #             'BOTTOM_LEFT': '{username}',
        #             'BOTTOM_CENTERED': '{asset}-{task}',
        #             'BOTTOM_RIGHT': '{current_frame}-{frame_end}',
        #             'filter': {
        #                 'families': [],
        #                 'tags': ['shotgridreview']
        #             }
        #         }


        #     print(repre)
        #     print(repre_burnin_defs)
        #     # Create copy of `_burnin_data` and `_temp_data` for repre.
        #     burnin_data = copy.deepcopy(_burnin_data)
        #     temp_data = copy.deepcopy(_temp_data)

        #     # Prepare representation based data.
        #     self.prepare_repre_data(instance, repre, burnin_data, temp_data)

        #     src_repre_staging_dir = repre["stagingDir"]
        #     # Should convert representation source files before processing?
        #     repre_files = repre["files"]
        #     if isinstance(repre_files, (tuple, list)):
        #         filename = repre_files[0]
        #     else:
        #         filename = repre_files

        #     first_input_path = os.path.join(src_repre_staging_dir, filename)
        #     # Determine if representation requires pre conversion for ffmpeg
        #     do_convert = should_convert_for_ffmpeg(first_input_path)
        #     # If result is None the requirement of conversion can't be
        #     #   determined
        #     if do_convert is None:
        #         self.log.info((
        #             "Can't determine if representation requires conversion."
        #             " Skipped."
        #         ))
        #         continue

        #     # Do conversion if needed
        #     #   - change staging dir of source representation
        #     #   - must be set back after output definitions processing
        #     if do_convert:
        #         new_staging_dir = get_transcode_temp_directory()
        #         repre["stagingDir"] = new_staging_dir

        #         convert_for_ffmpeg(
        #             first_input_path,
        #             new_staging_dir,
        #             _temp_data["frameStart"],
        #             _temp_data["frameEnd"],
        #             self.log
        #         )

        #     # Add anatomy keys to burnin_data.
        #     filled_anatomy = anatomy.format_all(burnin_data)
        #     burnin_data["anatomy"] = filled_anatomy.get_solved()

        #     # Add context data burnin_data.
        #     burnin_data["custom"] = (
        #         instance.data.get("custom_burnin_data") or {}
        #     )

        #     # Add source camera name to burnin data
        #     camera_name = repre.get("camera_name")
        #     if camera_name:
        #         burnin_data["camera_name"] = camera_name

        #     first_output = True

        #     files_to_delete = []
        #     for filename_suffix, burnin_def in repre_burnin_defs.items():
        #         new_repre = copy.deepcopy(repre)
        #         new_repre["stagingDir"] = src_repre_staging_dir

        #         # Keep "ftrackreview" tag only on first output
        #         if first_output:
        #             first_output = False
        #         elif "ftrackreview" in new_repre["tags"]:
        #             new_repre["tags"].remove("ftrackreview")

        #         burnin_values = {}
        #         for key in self.positions:
        #             value = burnin_def.get(key)
        #             if value:
        #                 burnin_values[key] = value.replace(
        #                     "{task}", "{task[name]}"
        #                 )

        #         # Remove "delete" tag from new representation
        #         if "delete" in new_repre["tags"]:
        #             new_repre["tags"].remove("delete")

        #         if len(repre_burnin_defs.keys()) > 1:
        #             # Update name and outputName to be
        #             # able have multiple outputs in case of more burnin presets
        #             # Join previous "outputName" with filename suffix
        #             new_name = "_".join(
        #                 [new_repre["outputName"], filename_suffix]
        #             )
        #             new_repre["name"] = new_name
        #             new_repre["outputName"] = new_name

        #         # Prepare paths and files for process.
        #         self.input_output_paths(
        #             repre, new_repre, temp_data, filename_suffix
        #         )

        #         # Data for burnin script
        #         script_data = {
        #             "input": temp_data["full_input_path"],
        #             "output": temp_data["full_output_path"],
        #             "burnin_data": burnin_data,
        #             "options": copy.deepcopy(burnin_options),
        #             "values": burnin_values,
        #             "full_input_path": temp_data["full_input_paths"][0],
        #             "first_frame": temp_data["first_frame"],
        #             "ffmpeg_cmd": new_repre.get("ffmpeg_cmd", "")
        #         }

        #         self.log.debug(
        #             "script_data: {}".format(json.dumps(script_data, indent=4))
        #         )

        #         # Store dumped json to temporary file
        #         temporary_json_file = tempfile.NamedTemporaryFile(
        #             mode="w", suffix=".json", delete=False
        #         )
        #         temporary_json_file.write(json.dumps(script_data))
        #         temporary_json_file.close()
        #         self.log.warning(temporary_json_file)
        #         self.log.warning(temporary_json_file.name)
        #         temporary_json_filepath = temporary_json_file.name.replace(
        #             "\\", "/"
        #         )

        #         # Prepare subprocess arguments
        #         args = list(executable_args)
        #         self.log.debug("Executing: {}".format(" ".join(args)))
        #         # Run burnin script
        #         process_kwargs = {
        #             "logger": self.log,
        #             "env": {}
        #         }
        #         if platform.system().lower() == "windows":
        #             process_kwargs["creationflags"] = CREATE_NO_WINDOW


        #         tmp_args = args + [temporary_json_filepath]
        #         run_openpype_process(*tmp_args, **process_kwargs)

        #         # Remove the temporary json
        #         os.remove(temporary_json_filepath)

        #         for filepath in temp_data["full_input_paths"]:
        #             filepath = filepath.replace("\\", "/")
        #             if filepath not in files_to_delete:
        #                 files_to_delete.append(filepath)

        #         # Add new representation to instance
        #         instance.data["representations"].append(new_repre)

        #     # Cleanup temp staging dir after procesisng of output definitions
        #     if do_convert:
        #         temp_dir = repre["stagingDir"]
        #         shutil.rmtree(temp_dir)
        #         # Set staging dir of source representation back to previous
        #         #   value
        #         repre["stagingDir"] = src_repre_staging_dir

        #     # Remove source representation
        #     # NOTE we maybe can keep source representation if necessary
        #     instance.data["representations"].remove(repre)

        #     self.log.debug("Files to delete: {}".format(files_to_delete))

        #     # Delete input files
        #     for filepath in files_to_delete:
        #         if os.path.exists(filepath):
        #             os.remove(filepath)
        #             self.log.debug("Removed: \"{}\"".format(filepath))

    def _get_burnin_options(self):
        # Prepare burnin options
        burnin_options = copy.deepcopy(self.default_options)
        if self.options:
            for key, value in self.options.items():
                if value is not None:
                    burnin_options[key] = copy.deepcopy(value)

        # Convert colors defined as list of numbers RGBA (0-255)
        # BG Color
        bg_color = burnin_options.get("bg_color")
        if bg_color and isinstance(bg_color, list):
            bg_red, bg_green, bg_blue, bg_alpha = bg_color
            bg_color_hex = "#{0:0>2X}{1:0>2X}{2:0>2X}".format(
                bg_red, bg_green, bg_blue
            )
            bg_color_alpha = float(bg_alpha) / 255
            burnin_options["bg_opacity"] = bg_color_alpha
            burnin_options["bg_color"] = bg_color_hex

        # FG Color
        font_color = burnin_options.get("font_color")
        if font_color and isinstance(font_color, list):
            fg_red, fg_green, fg_blue, fg_alpha = font_color
            fg_color_hex = "#{0:0>2X}{1:0>2X}{2:0>2X}".format(
                fg_red, fg_green, fg_blue
            )
            fg_color_alpha = float(fg_alpha) / 255
            burnin_options["opacity"] = fg_color_alpha
            burnin_options["font_color"] = fg_color_hex

        # Define font filepath
        # - font filepath may be defined in settings
        font_filepath = burnin_options.get("font_filepath")
        if font_filepath and isinstance(font_filepath, dict):
            sys_name = platform.system().lower()
            font_filepath = font_filepath.get(sys_name)

        if font_filepath and isinstance(font_filepath, six.string_types):
            font_filepath = font_filepath.format(**os.environ)
            if not os.path.exists(font_filepath):
                font_filepath = None

        # Use OpenPype default font
        if not font_filepath:
            font_filepath = openpype.api.resources.get_liberation_font_path()

        burnin_options["font"] = font_filepath

        return burnin_options

    def prepare_basic_data(self, instance):
        """Pick data from instance for processing and for burnin strings.

        Args:
            instance (Instance): Currently processed instance.

        Returns:
            tuple: `(burnin_data, temp_data)` - `burnin_data` contain data for
                filling burnin strings. `temp_data` are for repre pre-process
                preparation.
        """
        self.log.debug("Prepring basic data for burnins")
        context = instance.context

        version = instance.data.get("version")
        if version is None:
            version = context.data.get("version")

        frame_start = instance.data.get("frameStart")
        if frame_start is None:
            self.log.warning(
                "Key \"frameStart\" is not set. Setting to \"0\"."
            )
            frame_start = 0
        frame_start = int(frame_start)

        frame_end = instance.data.get("frameEnd")
        if frame_end is None:
            self.log.warning(
                "Key \"frameEnd\" is not set. Setting to \"1\"."
            )
            frame_end = 1
        frame_end = int(frame_end)

        handles = instance.data.get("handles")
        if handles is None:
            handles = context.data.get("handles")
            if handles is None:
                handles = 0

        handle_start = instance.data.get("handleStart")
        if handle_start is None:
            handle_start = context.data.get("handleStart")
            if handle_start is None:
                handle_start = handles

        handle_end = instance.data.get("handleEnd")
        if handle_end is None:
            handle_end = context.data.get("handleEnd")
            if handle_end is None:
                handle_end = handles

        frame_start_handle = frame_start - handle_start
        frame_end_handle = frame_end + handle_end

        burnin_data = copy.deepcopy(instance.data["anatomyData"])

        if "slate.farm" in instance.data["families"]:
            frame_start_handle += 1

        burnin_data.update({
            "version": int(version),
            "comment": context.data.get("comment") or ""
        })

        intent_label = context.data.get("intent") or ""
        if intent_label and isinstance(intent_label, dict):
            value = intent_label.get("value")
            if value:
                intent_label = intent_label["label"]
            else:
                intent_label = ""

        burnin_data["intent"] = intent_label

        temp_data = {
            "frame_start": frame_start,
            "frame_end": frame_end,
            "frame_start_handle": frame_start_handle,
            "frame_end_handle": frame_end_handle
        }

        self.log.debug(
            "Basic burnin_data: {}".format(json.dumps(burnin_data, indent=4))
        )

        return burnin_data, temp_data

    def repres_is_valid(self, repre):
        """Validation if representaion should be processed.

        Args:
            repre (dict): Representation which should be checked.

        Returns:
            bool: False if can't be processed else True.
        """

        if "burnin" not in repre.get("tags", []):
            self.log.info((
                "Representation '{}' don't have 'burnin' tag. Skipped."
            ).format(repre["name"]))
            return False

        if not repre.get("files"):
            self.log.warning((
                "Representation '{}' have empty files. Skipped."
            ).format(repre["name"]))
            return False
        return True

    def filter_burnins_by_tags(self, burnin_defs, tags):
        """Filter burnin definitions by entered representation tags.

        Burnin definitions without tags filter are marked as valid.

        Args:
            outputs (list): Contain list of burnin definitions from presets.
            tags (list): Tags of processed representation.

        Returns:
            list: Containg all burnin definitions matching entered tags.
        """
        filtered_burnins = {}
        repre_tags_low = set(tag.lower() for tag in tags)
        for filename_suffix, burnin_def in burnin_defs.items():
            valid = True
            tag_filters = burnin_def["filter"]["tags"]
            if tag_filters:
                # Check tag filters
                tag_filters_low = set(tag.lower() for tag in tag_filters)

                valid = bool(repre_tags_low & tag_filters_low)

            if valid:
                filtered_burnins[filename_suffix] = burnin_def

        return filtered_burnins

    def input_output_paths(
        self, src_repre, new_repre, temp_data, filename_suffix
    ):
        """Prepare input and output paths for representation.

        Store data to `temp_data` for keys "full_input_path" which is full path
        to source files optionally with sequence formatting,
        "full_output_path" full path to otput with optionally with sequence
        formatting, "full_input_paths" list of all source files which will be
        deleted when burnin script ends, "repre_files" list of output
        filenames.

        Args:
            new_repre (dict): Currently processed new representation.
            temp_data (dict): Temp data of representation process.
            filename_suffix (str): Filename suffix added to inputl filename.

        Returns:
            None: This is processing method.
        """
        # TODO we should find better way to know if input is sequence
        input_filenames = new_repre["files"]
        is_sequence = False
        if isinstance(input_filenames, (tuple, list)):
            if len(input_filenames) > 1:
                is_sequence = True

        # Sequence must have defined first frame
        # - not used if input is not a sequence
        first_frame = None
        if is_sequence:
            collections, _ = clique.assemble(input_filenames, minimum_items=1, patterns=[r'.+\.{}\..+'.format(clique.DIGITS_PATTERN)])
            if not collections:
                is_sequence = False
            else:
                input_filename = new_repre["sequence_file"]
                collection = collections[0]
                indexes = list(collection.indexes)
                padding = len(str(max(indexes)))
                head = collection.format("{head}")
                tail = collection.format("{tail}")
                output_filename = "{}%{:0>2}d{}{}".format(
                    head, padding, filename_suffix, tail
                )
                repre_files = []
                for idx in indexes:
                    repre_files.append(output_filename % idx)

                first_frame = min(indexes)
        else:
            input_filename = input_filenames
            for f in input_filenames:
                filepart_start, ext = os.path.splitext(input_filename)
                dir_path, basename = os.path.split(filepart_start)
                output_filename = basename + filename_suffix + ext
                if dir_path:
                    output_filename = os.path.join(dir_path, output_filename)

                repre_files = output_filename

        src_stagingdir = src_repre["stagingDir"]
        dst_stagingdir = new_repre["stagingDir"]
        full_input_path = os.path.join(
            os.path.normpath(src_stagingdir), input_filename
        ).replace("\\", "/")
        full_output_path = os.path.join(
            os.path.normpath(dst_stagingdir), output_filename
        ).replace("\\", "/")

        temp_data["full_input_path"] = full_input_path
        temp_data["full_output_path"] = full_output_path
        temp_data["first_frame"] = first_frame

        new_repre["files"] = repre_files

        self.log.debug("full_input_path: {}".format(full_input_path))
        self.log.debug("full_output_path: {}".format(full_output_path))

        # Prepare full paths to input files and filenames for reprensetation
        full_input_paths = []
        if is_sequence:
            for filename in input_filenames:
                filepath = os.path.join(
                    os.path.normpath(src_stagingdir), filename
                ).replace("\\", "/")
                full_input_paths.append(filepath)

        else:
            full_input_paths.append(full_input_path)

        temp_data["full_input_paths"] = full_input_paths

    def prepare_repre_data(self, instance, repre, burnin_data, temp_data):
        """Prepare data for representation.

        Args:
            instance (Instance): Currently processed Instance.
            repre (dict): Currently processed representation.
            burnin_data (dict): Copy of basic burnin data based on instance
                data.
            temp_data (dict): Copy of basic temp data
        """
        # Add representation name to burnin data
        burnin_data["representation"] = repre["name"]

        # no handles switch from profile tags
        if "no-handles" in repre["tags"]:
            burnin_frame_start = temp_data["frame_start"]
            burnin_frame_end = temp_data["frame_end"]

        else:
            burnin_frame_start = temp_data["frame_start_handle"]
            burnin_frame_end = temp_data["frame_end_handle"]

        burnin_duration = burnin_frame_end - burnin_frame_start + 1

        burnin_data.update({
            "frame_start": burnin_frame_start,
            "frame_end": burnin_frame_end,
            "duration": burnin_duration,
        })
        temp_data["duration"] = burnin_duration

        # Add values for slate frames
        burnin_slate_frame_start = burnin_frame_start

        # Move frame start by 1 frame when slate is used.
        if (
            "slate" in instance.data["families"]
            and "slate-frame" in repre["tags"]
        ):
            burnin_slate_frame_start -= 1

        self.log.debug("burnin_slate_frame_start: {}".format(
            burnin_slate_frame_start
        ))

        burnin_data.update({
            "slate_frame_start": burnin_slate_frame_start,
            "slate_frame_end": burnin_frame_end,
            "slate_duration": (
                burnin_frame_end - burnin_slate_frame_start + 1
            )
        })

    def main_family_from_instance(self, instance):
        """Return main family of entered instance."""
        return instance.data.get("family") or instance.data["families"][0]
