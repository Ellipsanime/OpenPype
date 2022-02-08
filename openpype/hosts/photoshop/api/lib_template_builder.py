from collections import OrderedDict
from . import stub as PhotoshopStub
from avalon.vendor import qargparse
import os
from openpype.tools.utils.widgets import OptionDialog
# from avalon.maya.pipeline import get_main_window

# To change as enum
build_types = ["context_asset", "linked_asset", "all_assets"]
stub = PhotoshopStub()


def get_placeholder_attributes(node):
    layers_by_id = stub.get_layers_metadata()
    return layers_by_id[str(node.id)]


def create_placeholder():
    args, _ = placeholder_window()
    options = OrderedDict()
    rewrite_enum_options(options, args)
    for arg in args:
        if not type(arg) == qargparse.Separator:
            options[str(arg)] = arg._data.get("items") or arg.read()

    if not options:
        return   # operation canceled, no locator created

    placeholder = stub.create_group('_TEMPLATE_PLACEHOLDER_')
    options.update({
        "id": "pyblish.avalon.instance",
        "family": "placeholder",
        "asset": os.environ.get("AVALON_ASSET", ""),
        "subset": "TEMPLATE_PLACEHOLDER",
        "active": False,
        "uuid": placeholder.id,
        "long_name": ""
    })
    # custom arg parse to force empty data query
    # and still imprint them on placeholder
    # and getting items when arg is of type Enumerator
    rewrite_enum_options(options, args)
    stub.imprint(placeholder, options)


def update_placeholder():
    placeholder = stub.get_selected_layers()
    if len(placeholder) == 0:
        raise ValueError("No node selected")
    if len(placeholder) > 1:
        raise ValueError("Too many selected nodes")
    placeholder = placeholder[0]

    args = placeholder_window(get_placeholder_attributes(placeholder))
    if not args:
        return  # operation canceled

    options = {str(arg): arg._data.get("items") or arg.read()
               for arg in args if not type(arg) == qargparse.Separator}
    options.update({
        "id": "pyblish.avalon.instance",
        "family": "placeholder",
        "asset": os.environ.get("AVALON_ASSET", ""),
        "subset": "TEMPLATE_PLACEHOLDER",
        "active": False,
        "uuid": placeholder.id,
        "long_name": ""
    })
    rewrite_enum_options(options, args)
    stub.imprint(placeholder, options)


def rewrite_enum_options(options, args):
    """
    Imprint method doesn't act properly with enums.
    Replacing the functionnality with this for now
    """
    options.update({str(arg): arg.read() for arg in args
                    if isinstance(arg, qargparse.Enum)})


def placeholder_window(options=None):
    options = options or dict()
    dialog = OptionDialog()
    dialog.setWindowTitle("Create Placeholder")

    args = [
        qargparse.Separator("Main attributes"),
        qargparse.Enum(
            "builder_type",
            label="Asset Builder Type",
            default=options.get("builder_type", 0),
            items=build_types,
            help="""Asset Builder Type
Builder type describe what template loader will look for.

context_asset : Template loader will look for subsets of
current context asset (Asset bob will find asset)

linked_asset : Template loader will look for assets linked
to current context asset.
Linked asset are looked in avalon database under field "inputLinks"
"""
        ),
        qargparse.String(
            "op_family",
            default=options.get("op_family", ""),
            label="OpenPype Family",
            placeholder="ex: model, look ..."),
        qargparse.String(
            "op_representation",
            default=options.get("op_representation", ""),
            label="OpenPype Representation",
            placeholder="ex: ma, abc ..."),
        qargparse.String(
            "loader",
            default=options.get("loader", ""),
            label="Loader",
            placeholder="ex: ReferenceLoader, LightLoader ...",
            help="""Loader

Defines what openpype loader will be used to load assets.
Useable loader depends on current host's loader list.
Field is case sensitive.
"""),
        qargparse.String(
            "loader_args",
            default=options.get("loader_args", ""),
            label="Loader Arguments",
            placeholder='ex: {"camera":"persp", "lights":True}',
            help="""Loader

Defines a dictionnary of arguments used to load assets.
Useable arguments depend on current placeholder Loader.
Field should be a valid python dict. Anything else will be ignored.
"""),
        qargparse.Integer(
            "order",
            default=options.get("order", 0),
            min=0,
            max=999,
            label="Order",
            placeholder="ex: 0, 100 ... (smallest order loaded first)",
            help="""Order

Order defines asset loading priority (0 to 999)
Priority rule is : "lowest is first to load"."""),
        qargparse.Separator(
            "Optional attributes"),
        qargparse.String(
            "asset_filter",
            default=options.get("asset_filter", ""),
            label="Asset filter",
            placeholder="regex filtering by asset name",
            help="Filtering assets by matching field regex to asset's name"),
        qargparse.String(
            "subset_filter",
            default=options.get("subset_filter", ""),
            label="Subset filter",
            placeholder="regex filtering by subset name",
            help="Filtering assets by matching field regex to subset's name"),
        qargparse.String(
            "hierarchy",
            default=options.get("hierarchy", ""),
            label="Hierarchy filter",
            placeholder="regex filtering by asset's hierarchy",
            help="Filtering assets by matching field asset's hierarchy")
    ]
    dialog.create(args)

    if not dialog.exec_():
        return None

    return args, dialog  # <- dialog here is a fix to avoid Garbage collector issue
