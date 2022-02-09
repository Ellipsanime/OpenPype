import avalon
from openpype.lib.abstract_template_loader import (
    AbstractTemplateLoader, AbstractPlaceholder)
from . import stub as PhotoshopStub
import tempfile

stub = PhotoshopStub()


class PhotoshopTemplateLoader(AbstractTemplateLoader):
    def import_template(self, template_path):
        print("Looking for ", template_path)
        stub.open(template_path)
        metadatas = stub.get_layers_metadata()
        all_layers = stub.get_layers()

        for layer_id, data in metadatas.items():
            if not data.get('asset', '') == '$ASSET':  # Ignore non placeholder
                continue
            data['asset'] = avalon.io.Session['AVALON_ASSET']
            layer = stub.get_layer(layer_id)
            stub.imprint(layer, data, all_layers=all_layers)
        # Save as temp file
        path = tempfile.NamedTemporaryFile().name
        stub.saveAs(image_path=path, ext='psd', as_copy=False)

    def get_loaded_containers_by_id(self):
        return super().get_loaded_containers_by_id()

    def get_template_nodes(self):
        return [node for _, node in stub.get_layers_metadata().items()
                if node['family'] == "placeholder"]

    def preload(self, placeholder, loaders_by_name, last_representation):
        placeholder_layer = stub.get_layer(placeholder.data['node']['uuid'])
        stub.select_layers([placeholder_layer])

    def load_succeed(self, placeholder, container):
        pass


class PhotoshopPlaceholder(AbstractPlaceholder):
    def parent_in_hierarchy(self, containers):
        return super().parent_in_hierarchy(containers)

    def get_data(self, node):
        layers_by_id = stub.get_layers_metadata()
        print(node)
        self.data = layers_by_id[str(node['uuid'])]['data']
        self.data["node"] = node

    def clean(self):
        return super().clean()

    def convert_to_db_filters(self, current_asset, linked_asset):
        if self.data['builder_type'] == "context_asset":
            return [{
                "type": "representation",
                "context.asset": {
                    "$eq": current_asset, "$regex": self.data['asset_filter']},
                "context.subset": {"$regex": self.data['subset_filter']},
                "context.hierarchy": {"$regex": self.data['hierarchy']},
                "context.representation": self.data['op_representation'],
                "context.family": self.data['op_family'],
            }]

        elif self.data['builder_type'] == "linked_asset":
            return [{
                "type": "representation",
                "context.asset": {
                    "$eq": asset_name, "$regex": self.data['asset_filter']},
                "context.subset": {"$regex": self.data['subset_filter']},
                "context.hierarchy": {"$regex": self.data['hierarchy']},
                "context.representation": self.data['op_representation'],
                "context.family": self.data['op_family'],
            } for asset_name in linked_asset]

        else:
            return [{
                "type": "representation",
                "context.asset": {"$regex": self.data['asset_filter']},
                "context.subset": {"$regex": self.data['subset_filter']},
                "context.hierarchy": {"$regex": self.data['hierarchy']},
                "context.representation": self.data['op_representation'],
                "context.family": self.data['op_family'],
            }]
