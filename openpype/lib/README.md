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

Add your template to OpenPype's configuration (at OpenPype Settings > Project Settings > `<Host>` > Templated Workfile Build Settings)
     
![image](https://user-images.githubusercontent.com/82808268/178286102-e9d09e3f-9efe-4097-a6e8-07fcca94bf16.png)

You can define a template by tasks and/or task types. Leaving a filter empty consider that any task or types will match.
So leaving task AND type empty will define a default template.
Template definition order is important, first template definition found with matching task and type will be used.
