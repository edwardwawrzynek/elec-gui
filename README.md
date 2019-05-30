A gui for interfacing with electronics instruments.

The GUI provides a means to acquire and display data captured from devices. It allows the configuration of options for each device, as well as for each channel associated with that device. It also provides the ability to display data from those channels on outputs (currently only matplotlib graphs).

```
                        Device Selection
                    Channel Selection
---------------------------------------------------------
device  |
wide    |
config  |
--------|
channel |                    data outputs
config  |
--------|
trigger |
config  |

```

## Dependencies
- python 3
- python gtk bindings (ubunt: `python3-gi python3-gi-cairo gir1.2-gtk-3.0`)
- numpy, xarray, matplotlib


## TODO
- Real device drivers (and async data collection)
- Live Preview of Channel Outputs
- Saving/Loading Device Configuration
- Saving/Loading interactive graphs
- Logic Analyzer Outputs on Graph
- Textual Outputs
- Operations on data (probably just another channel)
- Saving/Loading Data collection