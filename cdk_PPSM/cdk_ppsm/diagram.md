### Data Structure diagram
```
graph TD
    A[sg_data (dict)]
    A --> B1["instance_name_1"]
    A --> B2["instance_name_2"]
    B1 --> C1[ports (list)]
    B1 --> C2[protocols (list)]
    C1 --> D1["[from_port, to_port]"]
    C1 --> D2["[from_port, to_port]"]
    C2 --> E1["TCP"]
    C2 --> E2["UDP"]
    B2 --> F1[ports (list)]
    B2 --> F2[protocols (list)]

```