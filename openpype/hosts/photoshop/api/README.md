# Photoshop Integration

## Setup

The Photoshop integration requires two components to work; `extension` and `server`.

### Extension

To install the extension download [Extension Manager Command Line tool (ExManCmd)](https://github.com/Adobe-CEP/Getting-Started-guides/tree/master/Package%20Distribute%20Install#option-2---exmancmd).

```
ExManCmd /install {path to avalon-core}\avalon\photoshop\extension.zxp
```

### Server

The easiest way to get the server and Photoshop launch is with:

```
python -c ^"import avalon.photoshop;avalon.photoshop.launch(""C:\Program Files\Adobe\Adobe Photoshop 2020\Photoshop.exe"")^"
```

`avalon.photoshop.launch` launches the application and server, and also closes the server when Photoshop exists.

## Usage

The Photoshop extension can be found under `Window > Extensions > Avalon`. Once launched you should be presented with a panel like this:

![Untitled](https://user-images.githubusercontent.com/82808268/178270457-48b26d19-81ec-4855-a310-566632006049.png)

- Build : load and build template given by OpenPype configuration (see https://github.com/Ellipsanime/OpenPype/blob/3.8.2-el12/openpype/lib/README.md)
- Save : save your work as a new work version
- Add sheet : Add a group layer to be extracted during snapshot and publish
- Sanity : Execute sanities and checks on current workfile
- Snapshot : To make a Version and present your work to supervisors
- Publish : To confirm the work and publish it on OpenPype and Shotgrid

## Workflow
/!\ This section only concern Ellipsanime's fork of OpenPype
The fork is mainly centered around Shotgrid

Artist Standard Workflow  
![Workflow](https://user-images.githubusercontent.com/82808268/178270678-eac1e14e-9c8c-42c7-a997-7e41e9fb9450.png)

Building loads a template and populate it with required assets representations (see https://github.com/Ellipsanime/OpenPype/blob/3.8.2-el12/openpype/lib/README.md)


Required and produced by each step:
![workflow_ellipse_openpype_full drawio (6)](https://user-images.githubusercontent.com/82808268/180746693-26a8d56a-e5cd-4147-8238-69fd7ef8758e.png)
*Shotgrid Leecher is a tool developed by Ellipsanime to bridge between OpenPype and Shotgrid databases (https://github.com/Ellipsanime/shotgrid-leecher)

## Developping

### Extension
When developing the extension you can load it [unsigned](https://github.com/Adobe-CEP/CEP-Resources/blob/master/CEP_9.x/Documentation/CEP%209.0%20HTML%20Extension%20Cookbook.md#debugging-unsigned-extensions).

When signing the extension you can use this [guide](https://github.com/Adobe-CEP/Getting-Started-guides/tree/master/Package%20Distribute%20Install#package-distribute-install-guide).

```
ZXPSignCmd -selfSignedCert NA NA Avalon Avalon-Photoshop avalon extension.p12
ZXPSignCmd -sign {path to avalon-core}\avalon\photoshop\extension {path to avalon-core}\avalon\photoshop\extension.zxp extension.p12 avalon
```

### Plugin Examples

These plugins were made with the [polly config](https://github.com/mindbender-studio/config). To fully integrate and load, you will have to use this config and add `image` to the [integration plugin](https://github.com/mindbender-studio/config/blob/master/polly/plugins/publish/integrate_asset.py).

#### Creator Plugin
```python
from avalon import photoshop


class CreateImage(photoshop.Creator):
    """Image folder for publish."""

    name = "imageDefault"
    label = "Image"
    family = "image"

    def __init__(self, *args, **kwargs):
        super(CreateImage, self).__init__(*args, **kwargs)
```

#### Collector Plugin
```python
import pythoncom

import pyblish.api


class CollectInstances(pyblish.api.ContextPlugin):
    """Gather instances by LayerSet and file metadata

    This collector takes into account assets that are associated with
    an LayerSet and marked with a unique identifier;

    Identifier:
        id (str): "pyblish.avalon.instance"
    """

    label = "Instances"
    order = pyblish.api.CollectorOrder
    hosts = ["photoshop"]
    families_mapping = {
        "image": []
    }

    def process(self, context):
        # Necessary call when running in a different thread which pyblish-qml
        # can be.
        pythoncom.CoInitialize()

        photoshop_client = PhotoshopClientStub()
        layers = photoshop_client.get_layers()
        layers_meta = photoshop_client.get_layers_metadata()
        for layer in layers:
            layer_data = photoshop_client.read(layer, layers_meta)

            # Skip layers without metadata.
            if layer_data is None:
                continue

            # Skip containers.
            if "container" in layer_data["id"]:
                continue

            # child_layers = [*layer.Layers]
            # self.log.debug("child_layers {}".format(child_layers))
            # if not child_layers:
            #     self.log.info("%s skipped, it was empty." % layer.Name)
            #     continue

            instance = context.create_instance(layer.name)
            instance.append(layer)
            instance.data.update(layer_data)
            instance.data["families"] = self.families_mapping[
                layer_data["family"]
            ]
            instance.data["publish"] = layer.visible

            # Produce diagnostic message for any graphical
            # user interface interested in visualising it.
            self.log.info("Found: \"%s\" " % instance.data["name"])
```

#### Extractor Plugin
```python
import os

import openpype.api
from avalon import photoshop


class ExtractImage(openpype.api.Extractor):
    """Produce a flattened image file from instance

    This plug-in takes into account only the layers in the group.
    """

    label = "Extract Image"
    hosts = ["photoshop"]
    families = ["image"]
    formats = ["png", "jpg"]

    def process(self, instance):

        staging_dir = self.staging_dir(instance)
        self.log.info("Outputting image to {}".format(staging_dir))

        # Perform extraction
        stub = photoshop.stub()
        files = {}
        with photoshop.maintained_selection():
            self.log.info("Extracting %s" % str(list(instance)))
            with photoshop.maintained_visibility():
                # Hide all other layers.
                extract_ids = set([ll.id for ll in stub.
                                   get_layers_in_layers([instance[0]])])

                for layer in stub.get_layers():
                    # limit unnecessary calls to client
                    if layer.visible and layer.id not in extract_ids:
                        stub.set_visible(layer.id, False)

                save_options = []
                if "png" in self.formats:
                    save_options.append('png')
                if "jpg" in self.formats:
                    save_options.append('jpg')

                file_basename = os.path.splitext(
                    stub.get_active_document_name()
                )[0]
                for extension in save_options:
                    _filename = "{}.{}".format(file_basename, extension)
                    files[extension] = _filename

                    full_filename = os.path.join(staging_dir, _filename)
                    stub.saveAs(full_filename, extension, True)

        representations = []
        for extension, filename in files.items():
            representations.append({
                "name": extension,
                "ext": extension,
                "files": filename,
                "stagingDir": staging_dir
            })
        instance.data["representations"] = representations
        instance.data["stagingDir"] = staging_dir

        self.log.info(f"Extracted {instance} to {staging_dir}")
```

#### Loader Plugin
```python
from avalon import api, photoshop

stub = photoshop.stub()


class ImageLoader(api.Loader):
    """Load images

    Stores the imported asset in a container named after the asset.
    """

    families = ["image"]
    representations = ["*"]

    def load(self, context, name=None, namespace=None, data=None):
        with photoshop.maintained_selection():
            layer = stub.import_smart_object(self.fname)

        self[:] = [layer]

        return photoshop.containerise(
            name,
            namespace,
            layer,
            context,
            self.__class__.__name__
        )

    def update(self, container, representation):
        layer = container.pop("layer")

        with photoshop.maintained_selection():
            stub.replace_smart_object(
                layer, api.get_representation_path(representation)
            )

        stub.imprint(
            layer, {"representation": str(representation["_id"])}
        )

    def remove(self, container):
        container["layer"].Delete()

    def switch(self, container, representation):
        self.update(container, representation)
```
For easier debugging of Javascript:
https://community.adobe.com/t5/download-install/adobe-extension-debuger-problem/td-p/10911704?page=1
Add --enable-blink-features=ShadowDOMV0,CustomElementsV0 when starting Chrome
then localhost:8078 (port set in `photoshop\extension\.debug`)

Or use Visual Studio Code https://medium.com/adobetech/extendscript-debugger-for-visual-studio-code-public-release-a2ff6161fa01 

Or install CEF client from https://github.com/Adobe-CEP/CEP-Resources/tree/master/CEP_9.x
## Resources
  - https://github.com/lohriialo/photoshop-scripting-python
  - https://www.adobe.com/devnet/photoshop/scripting.html
  - https://github.com/Adobe-CEP/Getting-Started-guides
  - https://github.com/Adobe-CEP/CEP-Resources


## Final User Documentation

### Summary ****

- Select Project, Asset and Task
- Launch Photoshop
- Open Studio Tools Menu

1. Build
2. Save Workfile
3. Add Sheet Group
[Work] 
4. Snapshot
5. Publish

---

### Select Asset and Task
![Open_OP](https://user-images.githubusercontent.com/2683717/179759699-b975de91-3241-4bc5-aed0-5a43097d1c15.gif)

### Launch Photoshop
![Launcher](https://user-images.githubusercontent.com/2683717/179761902-274e1959-8095-4a39-bb52-bb0de93b6116.gif)

### Open Studio Tool
![Untitled](https://user-images.githubusercontent.com/2683717/179761558-5db528a8-6ac4-4f6e-83fe-a50622176e81.png)

### 1. 2. Build and Save
![Build](https://user-images.githubusercontent.com/2683717/179761711-6ab2a403-d6a8-43b9-a319-775a24a70009.gif)

### 3. Add Sheet Group, and the work...
![AddSheet](https://user-images.githubusercontent.com/2683717/179761647-af81fd90-048b-43d4-a9d6-8048422e4e32.gif)

### 4. Snapshot
![Snap](https://user-images.githubusercontent.com/2683717/179761594-c58311a3-3965-4e2f-a8ff-578ca91036dd.gif)

### 5. Publish
![Pub](https://user-images.githubusercontent.com/2683717/179761618-12187bc4-04e3-49d2-a429-c131bb411f0d.gif)




### Build

Choose the task that is assigned to you then click on the Photoshop icon.

![Untitled (1)](https://user-images.githubusercontent.com/2683717/179763322-b4566680-37c9-4dc3-9e22-942a8cf47c80.png)

Studio Tools menu opens after a few seconds

![Untitled (2)](https://user-images.githubusercontent.com/2683717/179763344-5845bf0e-4f2b-4786-af58-cedf3bfa9844.png)

Studio Tools buttons are displayed in the order you should proceed

Start with a Build. 
It will import previous task’s published sheets. 
Becareful with the first task (rough) as the build won’t import any sheet because well, there's no previous one.

Once the build is over this window appears.

![Untitled (3)](https://user-images.githubusercontent.com/2683717/179763406-98e0b023-e151-4f14-b159-84cea1bfa01e.png)

Published sheets are in the REFS group.

![Untitled (4)](https://user-images.githubusercontent.com/2683717/179763444-c2db000a-1819-4885-8cdb-e7cc85e9c3d2.png)

So you have a document named `untitled.psd` that needs to be saved.

In Studio Tools, click on `Save workfile`, then on `OK`. 
With `Next Available` version checked, your file will automaticaly update version. 
It can be unchecked in order to choose the specific number you want. 
You can also choose the extension type; default is `PSD`. 

![Untitled (5)](https://user-images.githubusercontent.com/2683717/179763488-01e91622-7947-444a-9b62-d8e72c6d6d57.png)

Your document is now saved. 
You can start creating new folder. 
To do that, click on `Add sheet`.
This creates a sheet group named `task<XXX>` ready for OpenPype export and sheet drawing.

![Untitled (6)](https://user-images.githubusercontent.com/2683717/179763520-b998a51b-9f4b-4637-b9b8-3e4187536c12.png)

Becareful: any sheet out of these folders won't be exported.

You can create as many groups as you need inside the main group. 
But keep in mind that all the contained sheets will be merged.

![Untitled (7)](https://user-images.githubusercontent.com/2683717/179763623-eb6ee33e-6d91-4dd1-9679-4fef914ac797.png)

### Sanity

At anytime you can do a sanity to check if everything is fine on your scene. 

![Untitled (8)](https://user-images.githubusercontent.com/2683717/179765375-22bd6fb3-c127-4ba4-a9ae-16b5a20090ed.png)

Click on `Sanity`

Once the collect over, choose which sanity you wan’t to make by clicking on the square under validate.

![Untitled (9)](https://user-images.githubusercontent.com/2683717/179765386-b87a49db-c4f2-499b-a16d-4ff29e1dcdf9.png)

Then click on `Play` `|>`

If everything is green, all is good.

![Untitled (10)](https://user-images.githubusercontent.com/2683717/179765397-889d292c-2ce1-4c8a-ac18-6febbb76b4dc.png)


### Presentation and Snapshot

Do you want to show your work to a supervisor? 

Open Studio Tools and click on `Snapshot`, the following window will appear.

![Untitled (8)](https://user-images.githubusercontent.com/2683717/179767931-4927d796-f051-4264-aaa4-01f995428ccd.png)

OpenPype will first gather the data then you just need to click on `Play` `|>`

![Untitled (9)](https://user-images.githubusercontent.com/2683717/179767948-60f3ca7f-e60f-445c-8fbe-890de7679ad2.png)

![Untitled (10)](https://user-images.githubusercontent.com/2683717/179767962-6a39d7bf-d532-4fc7-82bc-765deeab2716.png)

_“Finished succesfully”_ should appear. 

A version is now available on Shotgrid with the status `pending review`. 

Making a snapshot creates automaticaly a new version `n+1`.


### Publish

Open the last approved `PSD`.

Then, in the Studio Tools menu, click on `Publish`

![Untitled (11)](https://user-images.githubusercontent.com/2683717/179770093-4b35f32d-89a3-4f12-8962-e420d9cb9d8a.png)

Once the collect is over, select the right status (`approved` or `confirmed`) and click on the `Play` `|>` button.

![Untitled (12)](https://user-images.githubusercontent.com/2683717/179770154-617f1614-fbef-4b76-b2b9-0dac651fe43f.png)
![Untitled (13)](https://user-images.githubusercontent.com/2683717/179770176-efd97ad2-5c38-442c-a5b4-4fc718baf9da.png)

The export is over. 

It is now available on Shotgrid and ready for the next task.

