# OpenPype Library


## Template loader

### Usage

```
from openpype.host.build_template import build_template
build_workfile_template()
```

### Developing

![UML](https://user-images.githubusercontent.com/82808268/178266969-0740e671-d40e-4de8-9c84-af3abdf75b4a.png)

Template loader load a template given by OpenPype configuration,
then create a number of placeholder depending on loaded template and concrete template loader implementation

(ie: MayaTemplateLoader create a placeholder for each node in template containing a special property,
     PhotoshopTemplateLoader create a placeholder for each layer id with special metadata)

Then each placeholder data is converted to a db_filter, a filter to find in Avalon the correct representation to load,
using 'loader' an OpenPype Loader.
