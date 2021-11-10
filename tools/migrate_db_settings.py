import json
import os
import logging
import argparse
import pprint
import sys
from itertools import chain, starmap
from typing import Dict, Any, Iterable, Tuple, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

AVALON_DB = "avalon"
OPENPYPE_DB = "openpype"


def _flatten_dict(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    dict_ = dictionary
    while True:
        dict_ = dict(
            chain.from_iterable(starmap(_unpack_nested, dict_.items()))
        )
        if not any(type(x) is dict for x in dict_.values()):
            return dict_


def _unpack_nested(
        key: str, value: Any, sep: str = "."
) -> Iterable[Tuple[str, Any]]:
    value_type = type(value)
    if value_type is dict:
        if not value:
            yield key, None
        for k, v in value.items():
            yield f"{key}{sep}{k}", v
    if value_type is not dict:
        yield key, value


class ProjectSettingsHandler:

    client: MongoClient
    project_name: str
    server_timeout: int = 1000
    avalon: Database
    openpype: Database

    def __init__(self, mongo_url: str, project_name: str):
        self.project_name = project_name
        self.client = MongoClient(mongo_url,
                                  serverSelectionTimeoutMS=self.server_timeout)
        self.avalon = self.client.get_database(AVALON_DB)
        self.openpype = self.client.get_database(OPENPYPE_DB)

    def ping(self) -> bool:
        try:
            self.avalon.command("ping")
            return True
        except ServerSelectionTimeoutError:
            return False

    def find_value_to_update(self, location, type,
                             template, name=None) -> Dict[str, Any]:
        col = self._get_collection(location)

        if col:
            req_filter = self._get_filter(location, type, name)
            entity = col.find_one(req_filter)
            return _flatten_dict(
                self._filter_entity_with_template(entity, template)
            )

        return {}

    def upsert(self, location, type, data, name=None):
        col = self._get_collection(location)

        if col:
            req_filter = self._get_filter(location, type, name)
            res = col.update_one(req_filter, {"$set": _flatten_dict(data)},
                                 upsert=True)

    def _get_collection(self, location) -> Optional[Collection]:
        if location == "avalon_project":
            return self.avalon.get_collection(self.project_name)
        elif location == "openpype_settings":
            return self.openpype.get_collection("settings")

    def _get_filter(self, location, type, name=None) -> Dict[str, Any]:
        req_filter = {"type": type}

        if name:
            name_key = None
            if location == "avalon_project":
                name_key = "name"
            elif location == "openpype_settings":
                name_key = "project_name"
            if name == "@project_name":
                name = self.project_name
            req_filter[name_key] = name

        return req_filter

    def _filter_entity_with_template(self, entity, template):
        if type(template) == bool and template:
            return entity

        if type(entity) == dict:
            filtered_entity = {}
            for k in entity.keys():
                if k in template.keys():
                    filtered_entity[k] = self._filter_entity_with_template(
                        entity[k], template[k])
            return filtered_entity


class Migrator:

    project_src: ProjectSettingsHandler
    project_dst: ProjectSettingsHandler
    configuration_path: str
    configuration: Dict[str, Any]
    logger: logging.Logger

    def __init__(self, project_src: ProjectSettingsHandler,
                 project_dst: ProjectSettingsHandler,
                 configuration_path: str):
        self.project_src = project_src
        self.project_dst = project_dst
        self.configuration_path = configuration_path
        self.log = logging.getLogger()

    def read_configuration(self) -> bool:
        self.log.info("Reading configuration ...")

        if not os.path.exists(args.conf_path):
            self.log.error(
                "Configuration file {} not found".format(args.conf_path))
            return False

        with open(self.configuration_path, "r") as f:
            self.configuration = json.load(f)

        if type(self.configuration) != list:
            self.log.error(
                "Configuration must be a list of object")
            return False

        return True

    def migrate(self):

        for target_setting in self.configuration:
            location = target_setting.get("location")
            entity_type = target_setting.get("type")
            name = target_setting.get("name")
            template = target_setting.get("template")
            self.log.info("Migrating {}, {}, {}".format(
                location,
                entity_type,
                target_setting.get("name", "")))

            value_to_migrate = self.project_src.find_value_to_update(
                location, entity_type, template, name
            )

            if not value_to_migrate:
                self.log.info("No data found to migrate")
            else:
                self.log.info("Value to migrate\n{}"
                              .format(pprint.pformat(value_to_migrate)))
                self.project_dst.upsert(location, entity_type,
                                        value_to_migrate, name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("mongo_uri_src", help="Address of mongodb source")
    parser.add_argument("project_src", help="Name of avalon project source")
    parser.add_argument("mongo_uri_dst", help="Address of mongodb destination")
    parser.add_argument("project_dst", help="Name of avalon project destination")
    parser.add_argument("conf_path", help="Path of json configuration template file")

    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    project_src = ProjectSettingsHandler(args.mongo_uri_src, args.project_src)
    if project_src.ping():
        logger.info("Migrating data from project {} on mongo {}".format(
            args.project_src, args.mongo_uri_src))
    else:
        logger.error("MongoDB {} not reachable".format(args.mongo_uri_src))
        sys.exit(1)

    project_dst = ProjectSettingsHandler(args.mongo_uri_dst, args.project_dst)
    if project_dst.ping():
        logger.info("to project {} on mongo {}".format(
            args.project_dst, args.mongo_uri_dst))
    else:
        logger.error("MongoDB {} not reachable".format(args.mongo_uri_dst))
        sys.exit(1)

    migrator = Migrator(project_src, project_dst, args.conf_path)
    if not migrator.read_configuration():
        sys.exit(1)
    else:
        logger.info("Configuration file : OK")

    migrator.migrate()
