import os
import sys
import json
import tempfile
import collections
import traceback

import ftrack_api

from pype.modules.ftrack.lib import (
    BaseAction,
    statics_icon
)


class PypeAppToolsPrep(BaseAction):
    """Helper action to convert new old values of tools and apps.
    Tools and Applications custom attributes must be changed and to keep
    values on entities we have to store their values before change of custom
    attribute's configurations. Then change configurations to match new way of
    applications and tools definitions. Then reapply the values.
    Action will ask for mapping of old value -> new value.
    """
    identifier = "pype.app.tools.preparation"
    label = "Pype Admin"
    variant = "- App & Tool values"
    description = (
        "Store values of tools_env and applications custom attributes."
    )

    role_list = ["Pypeclub"]
    icon = statics_icon("ftrack", "action_icons", "PypeAdmin.svg")

    # Something like constants
    action_key = "__action__"
    tools_key = "tools_env"
    app_key = "applications"
    pop_key = "__pop___"
    # Filename of temp file
    output_filename = "app_tool_values.json"

    def discover(self, session, entities, event):
        # Ignore entities that are not tasks or projects
        for ent in event["data"]["selection"]:
            if ent["entityType"].lower() in ["show", "task"]:
                return True
        return False

    def interface(self, session, entities, event):
        values = event["data"].get("values")
        if values:
            return

        items = []
        items.append({
            "type": "label",
            "value": (
                "<b>This action is for conversion of values for applications"
                " and tools.</b><br/>Please choose if want to store current"
                " values or restore them.<br/><i><b>NOTE:</b>To be able"
                " restore you have to have already stored.</i>"
            )
        })

        items.append({"type": "label", "value": "---"})

        # How many versions to keep
        items.append({
            "label": "Action",
            "type": "enumerator",
            "name": self.action_key,
            "value": "store_values",
            "data": [
                {
                    "label": "1.) Store values",
                    "value": "store_values"
                }, {
                    "label": "2.) Convert pype-config",
                    "value": "convert_pype_config"
                }, {
                    "label": "3.) Trigger Create/Update Custom Attributes",
                    "value": "create_update_cust_attrs"
                }, {
                    "label": "4.) Restore values",
                    "value": "restore_values"
                }
            ]
        })

        return {
            "items": items,
            "title": "Store or Restore app/tool values"
        }

    def launch(self, session, entities, event):
        values = event["data"].get("values")
        if not values:
            return

        action_name = values.get(self.action_key)
        if action_name == "store_values":
            return self.store_values(session, event)

        elif action_name == "convert_pype_config":
            return self.convert_pype_config(session, event)

        elif action_name == "create_update_cust_attrs":
            return self.trigger_create_update_cust_attrs(session, event)

        elif action_name == "restore_values":
            return self.restore_values(session, event)

        return {
            "success": False,
            "message": "Unknown action \"{}\"".format(action_name)
        }

    def _app_tools_mapping_items(self, event, invalid_apps, invalid_tools):
        if not invalid_apps and not invalid_tools:
            return {}, {}, {}

        values = event["data"]["values"]

        invalid_apps_mapping = {}
        all_valid = True
        for app_name in invalid_apps:
            values_key = "__app__{}".format(app_name)
            if values_key in values:
                value = values[values_key]
                if "_" not in value:
                    all_valid = False
                invalid_apps_mapping[app_name] = value
            else:
                all_valid = False

        invalid_tools_mapping = {}
        for tool_name in invalid_tools:
            values_key = "__tool__{}".format(tool_name)
            if values_key in values:
                value = values[values_key]
                if "_" not in value:
                    all_valid = False
                invalid_tools_mapping[tool_name] = value
            else:
                all_valid = False

        if all_valid:
            return {}, invalid_apps_mapping, invalid_tools_mapping

        items = []
        items.append({
            "type": "hidden",
            "name": self.action_key,
            "value": "convert_pype_config"
        })
        items.append({
            "type": "label",
            "value": (
                "## Config contain application or tool names"
                " that do not contain underscore."
            )
        })
        if invalid_apps_mapping or invalid_tools_mapping:
            items.append({
                "type": "label",
                "value": (
                    "<b>WARNING:</b> You've entered some invalid values."
                    " Please check again."
                )
            })
        if invalid_apps:
            items.append({"type": "label", "value": "---"})
            items.append({
                "type": "label",
                "value": "### Applications"
            })
            for app_name in invalid_apps:
                values_key = "__app__{}".format(app_name)
                value = invalid_apps_mapping.get(app_name) or app_name
                items.append({
                    "label": app_name,
                    "type": "text",
                    "name": values_key,
                    "value": value,
                    "placeholder": (
                        "Enter new name of application with underscore."
                    )
                })

        if invalid_tools:
            items.append({"type": "label", "value": "---"})
            items.append({
                "type": "label",
                "value": "### Tools"
            })

            for tool_name in invalid_tools:
                values_key = "__tool__{}".format(tool_name)
                value = invalid_tools_mapping.get(tool_name) or tool_name
                items.append({
                    "label": tool_name,
                    "type": "text",
                    "name": values_key,
                    "value": value,
                    "placeholder": "Enter new name of tool with underscore."
                })
        items_data = {
            "items": items,
            "title": "New tools and apps mappings"
        }
        return items_data, invalid_apps_mapping, invalid_tools_mapping

    def convert_pype_config(self, session, event):
        values = event["data"]["values"]

        pype_config_dir = os.environ["PYPE_CONFIG"]
        environments_dir = os.path.join(pype_config_dir, "environments")
        launchers_dir = os.path.join(pype_config_dir, "launchers")
        global_presets_dir = os.path.join(
            pype_config_dir, "presets", "global"
        )
        applications_filepath = os.path.join(
            global_presets_dir, "applications.json"
        )
        tools_filepath = os.path.join(
            global_presets_dir, "tools.json"
        )

        applications_data = {}
        if os.path.exists(applications_filepath):
            with open(applications_filepath, "r") as file_stream:
                applications_data = json.load(file_stream)

        tools_data = {}
        if os.path.exists(tools_filepath):
            with open(tools_filepath, "r") as file_stream:
                tools_data = json.load(file_stream)

        invalid_apps = [
            app_name
            for app_name in applications_data.keys()
            if "_" not in app_name
        ]
        invalid_tools = [
            tool_name
            for tool_name in tools_data.keys()
            if "_" not in tool_name
        ]

        items_data, invalid_apps_mapping, invalid_tools_mapping = (
            self._app_tools_mapping_items(event, invalid_apps, invalid_tools)
        )
        if items_data:
            return items_data

        if applications_data:
            new_data = {}
            for key, value in applications_data.items():
                if key not in invalid_apps_mapping:
                    new_key = key.replace(".", "-")
                else:
                    # Skip key if mapping was not set
                    new_key = invalid_apps_mapping[key].replace(".", "-")
                    if not new_key:
                        continue

                new_data[new_key] = value

            with open(applications_filepath, "w") as file_stream:
                json.dump(new_data, file_stream, indent=4)

        if tools_data:
            new_data = {}
            for key, value in tools_data.items():
                if key not in invalid_tools_mapping:
                    new_key = key.replace(".", "-")
                else:
                    # Skip key if mapping was not set
                    new_key = invalid_tools_mapping[key].replace(".", "-")
                    if not new_key:
                        continue
                new_data[new_key] = value

            with open(tools_filepath, "w") as file_stream:
                json.dump(new_data, file_stream, indent=4)

        for filename in os.listdir(environments_dir):
            basename, ext = os.path.splitext(filename)
            if not ext:
                continue

            if basename in invalid_apps_mapping:
                basename = invalid_apps_mapping[basename]

            elif basename in invalid_tools_mapping:
                basename = invalid_tools_mapping[basename]

            if not basename:
                continue

            new_filename = basename.replace(".", "-") + ext

            old_filepath = os.path.join(environments_dir, filename)
            new_filepath = os.path.join(environments_dir, new_filename)
            os.rename(old_filepath, new_filepath)

        for filename in os.listdir(launchers_dir):
            basename, ext = os.path.splitext(filename)
            if ext != ".toml":
                continue

            if basename in invalid_apps_mapping:
                basename = invalid_apps_mapping[basename]
                if not basename:
                    continue

            new_filename = basename.replace(".", "-") + ext
            if new_filename == filename:
                continue

            old_filepath = os.path.join(launchers_dir, filename)
            new_filepath = os.path.join(launchers_dir, new_filename)
            os.rename(old_filepath, new_filepath)

    def trigger_create_update_cust_attrs(self, session, event):
        self.trigger_action("create.update.attributes", event)

    def store_values(self, session, event):
        user_id = event["source"]["user"]["id"]
        user = session.query("User where id is \"{}\"".format(user_id)).one()

        job_entity = session.create("Job", {
            "user": user,
            "status": "running",
            "data": json.dumps({
                "description": "Storing app & tool values."
            })
        })
        session.commit()
        try:
            self._store_values(session, event, job_entity)

        except Exception:
            exc_info = sys.exc_info()

            self.log.warning("Storing of values crashed.", exc_info=True)

            self._add_traceback_report(job_entity, session, exc_info)
            job_entity["status"] = "failed"
            job_entity["data"] = json.dumps({
                "description": "Failed to store app & tool values."
            })
            session.commit()

        return True

    def _add_traceback_report(self, job_entity, session, exc_info):
        traceback_text = "\n".join(traceback.format_exception(*exc_info))
        tmp_path = os.path.join(
            tempfile.mkdtemp(),
            "error.txt"
        )
        with open(tmp_path, "w") as file_stream:
            file_stream.write(traceback_text)

        self.add_component_to_job(job_entity, session, tmp_path, "Traceback")

        # Remove temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    def _store_values(self, session, event, job_entity):
        data = self.get_app_tool_values(session)
        json_file_path = os.path.join(
            tempfile.mkdtemp(),
            self.output_filename
        )
        with open(json_file_path, "w") as file_stream:
            json.dump(data, file_stream, indent=4)

        self.add_component_to_job(job_entity, session, json_file_path)

        job_entity["status"] = "done"
        job_entity["data"] = json.dumps({
            "description": "Values of app & tool are ready."
        })

        session.commit()

        # Remove temp file
        if os.path.exists(json_file_path):
            os.remove(json_file_path)

    def add_component_to_job(
        self, job_entity, session, source_filepath, filename=None
    ):
        if filename is None:
            filename = os.path.splitext(os.path.basename(source_filepath))[0]

        session._configure_locations()
        location = session.query(
            "Location where name is \"ftrack.server\""
        ).one()

        component = session.create_component(
            source_filepath,
            data={"name": filename},
            location=location
        )
        session.create(
            "JobComponent",
            {
                "component_id": component["id"],
                "job_id": job_entity["id"]
            }
        )

        session.commit()

    def get_app_tool_values(self, session):
        # Prepare custom attribute configurations
        confs = session.query((
            "select id, key"
            " from CustomAttributeConfiguration"
            " where key in (\"{}\", \"{}\")"
        ).format(self.app_key, self.tools_key)).all()
        conf_id_by_ids = {
            conf["id"]: conf
            for conf in confs
        }

        # table_name = "ContextCustomAttributeValue"
        # Only really set values
        table_name = "CustomAttributeValue"
        cust_attr_query = (
            "select value, configuration_id, entity_id"
            " from {}"
            " where configuration_id in ({})"
        ).format(
            table_name,
            ",".join(['"{}"'.format(value) for value in conf_id_by_ids.keys()])
        )

        call_expr = [{
            "action": "query",
            "expression": cust_attr_query
        }]
        call_method = getattr(session, "call", getattr(session, "_call", None))
        [query_items] = call_method(call_expr)

        data = collections.defaultdict(dict)
        for item in query_items["data"]:
            entity_id = item["entity_id"]
            conf_id = item["configuration_id"]
            conf = conf_id_by_ids[conf_id]

            value = item["value"]
            data[entity_id][conf["key"]] = value

        return data

    def restore_values(self, session, event):
        values = event["data"]["values"]
        path = values.get("path")
        if path and os.path.exists(path):
            return self._restore_values(session, event, path)

        if "path" not in values:
            label = "Please enter path to your json file with stored values:"
        else:
            label = (
                "<b>Path you've entered is not valid</b><br/>- {}<br/><br/>"
                "<br/>Please enter a valid path to your json file with stored"
                " values:"
            ).format(path)

        items = []
        items.append({
            "type": "hidden",
            "name": self.action_key,
            "value": "restore_values"
        })
        items.append({
            "type": "label",
            "value": label
        })
        items.append({
            "label": "Path to json file",
            "type": "text",
            "name": "path"
        })
        return {
            "items": items,
            "title": "Enter path to json file with stored values"
        }

    def _mapping_to_values(self, session, confs, json_data, event):
        event_values = event["data"]["values"]

        conf_id_by_key = {
            conf["key"]: conf["id"]
            for conf in confs
        }
        for entity_id, key_values in json_data.items():
            for key, value in key_values.items():
                conf_id = conf_id_by_key.get(key)
                if not conf_id:
                    continue

                new_value = []
                for item in value:
                    mapped_item = event_values.get(item)
                    if mapped_item != self.pop_key:
                        new_value.append(mapped_item)

                entity_def = collections.OrderedDict()
                entity_def["configuration_id"] = conf_id
                entity_def["entity_id"] = entity_id

                session.recorded_operations.push(
                    ftrack_api.operation.UpdateEntityOperation(
                        "ContextCustomAttributeValue",
                        entity_def,
                        "value",
                        ftrack_api.symbol.NOT_SET,
                        new_value
                    )
                )
        session.commit()
        return {
            "success": True,
            "message": "Mapping has finished"
        }

    def _restore_values(self, session, event, path):
        event_values = event["data"]["values"]
        mapping_part = event_values.get("mapping_part")

        with open(path, "r") as file_stream:
            json_data = json.load(file_stream)

        tool_items = set()
        app_items = set()
        for env_values in json_data.values():
            for item in env_values.get(self.app_key) or []:
                app_items.add(item)

            for item in env_values.get(self.tools_key) or []:
                tool_items.add(item)

        if not app_items and not tool_items:
            msg = "Nothing to restore from entered json. {}".format(path)
            self.log.info(msg)
            return {
                "success": True,
                "message": msg
            }

        confs = session.query((
            "select id, key, config"
            " from CustomAttributeConfiguration"
            " where key in (\"{}\", \"{}\")"
        ).format(self.app_key, self.tools_key)).all()
        missing_keys = {self.tools_key, self.app_key}
        for conf in confs:
            conf_items = json.loads(json.loads(conf["config"])["data"])
            variants = set()
            for item in conf_items:
                variants.add(item["value"])

            if conf["key"] == self.tools_key:
                tool_variants = variants
            elif conf["key"] == self.app_key:
                app_variants = variants

            missing_keys.remove(conf["key"])

        if missing_keys:
            msg = (
                "Couldn't find custom attribute configurations with key {}"
            ).format(" or ".join(
                ["\"{}\"".format(key) for key in missing_keys]
            ))
            self.log.warning(msg)
            return {
                "success": False,
                "message": msg
            }

        if mapping_part:
            return self._mapping_to_values(session, confs, json_data, event)

        items = [{
            "type": "hidden",
            "name": "mapping_part",
            "value": "1"
        }]
        for key, value in event_values.items():
            items.append({
                "type": "hidden",
                "name": key,
                "value": value
            })

        tools_data = [{
            "label": "< Pop >",
            "value": self.pop_key
        }]
        for tool_variant in sorted(tool_variants):
            tools_data.append({
                "label": tool_variant,
                "value": tool_variant
            })

        items.append({
            "type": "label",
            "value": "Tools:"
        })
        for tool_item in sorted(tool_items):
            item = {
                "label": tool_item,
                "name": tool_item,
                "type": "enumerator",
                "value": self.pop_key,
                "data": tools_data
            }
            if tool_item not in tool_variants:
                tool_item = tool_item.replace(".", "-")
            if tool_item not in tool_variants:
                listed_str = list(tool_item)
                if "_" in listed_str:
                    idx = listed_str.index("_")
                    listed_str[idx] = "/"
                    tool_item = "".join(listed_str)

            if tool_item in tool_variants:
                item["value"] = tool_item
            items.append(item)

        items.append({"type": "label", "value": "---"})
        items.append({
            "type": "label",
            "value": "Applications:"
        })
        apps_data = [{
            "label": "< Pop >",
            "value": self.pop_key
        }]
        for app_variant in sorted(app_variants):
            apps_data.append({
                "label": app_variant,
                "value": app_variant
            })
        for app_item in sorted(app_items):
            item = {
                "label": app_item,
                "name": app_item,
                "type": "enumerator",
                "value": self.pop_key,
                "data": apps_data
            }
            if app_item not in tool_variants:
                app_item = app_item.replace(".", "-")
                if "_" in app_item:
                    item_parts = app_item.split("_")
                    group_name = item_parts.pop(0)
                    app_item = "/".join((group_name, "_".join(item_parts)))

            if app_item in app_variants:
                item["value"] = app_item
            items.append(item)
        return {
            "items": items,
            "title": "Tools and apps mappings"
        }


def register(session, plugins_presets={}):
    '''Register plugin. Called when used as an plugin.'''

    PypeAppToolsPrep(session, plugins_presets).register()
