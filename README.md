# LilyPanel
A simple Python GUI that sends VMC data to make toggles easier in [Inochi Session](https://github.com/Inochi2D/inochi-session). Should be compatible with any VMC application, but this program is tailored for Inochi Session.

## License
All *source-code* (does not include assets) is licensed BSD-2.

## Executing from Source
If you want to execute the program from the Python source, you will need to install the `pythonosc` library. This can be done through the console command:  
```
pip install pythonosc
```

## Setup
All settings are set via editing the file `lilypanel.json`.

### Connection
The IP defaults to 127.0.0.1 (localhost).  
The port defaults to 39540.

To change either of these, find the `ip` and `port` fields at the top of the settings file.
```json
{
    "ip": "127.0.0.1",
    "port": 39540
}
```
The ip must be enclosed in "quotes" or 'apostrophies'.  
The port must be an integer.

#### Inochi Session
Do not change the IP address, Inochi Session expects to receive data via localhost.  
If your Virtual Space does not already have one, add a VMC receiver to it with the corresponding port. (Multiple VMC applications may share the same port, as such you may skip this step if already using PuppetString.)

### Layout
To change how the control panel is layed out, modify the layout object.

Default:
```json
"layout": {
    "buttons": {
        "columns": 2,
        "xPadding": 3,
        "yPadding": 1
    },
    "sliders": {
        "columns": 2,
        "xPadding": 3,
        "yPadding": 1,
        "orientation": "vertical"
    },
    "xPadding": 20,
    "yPadding": 5
}
```

- Columns refers to the number of columns per button/slider. When no columns are left, a new row is created on the user interface.
- xPadding refers to have much space should be between individual elements along the x-axis.
- yPadding refers to have much space should be between individual elements along the y-axis.
- Slider orientation accepts either `"vertical"` or `"horizontal"`.
- The overall padding affects the distance between the button side and the slider side. (Also affects distance between them and the borders of the program.)

### BlendShapes
An unlimited number of blendshapes can be registered to the program. All blendshapes should be given unique names and not clash with those of other programs.  
By default, 8 example blendshape are provided. These serve as a guide on how to add your own and should be removed.

All blendshapes should be a json object added to the `"blends"` array.

#### Toggles
Toggles require 4 fields. The button will default to the off state.  
Values may be integers or contain decimals.

To add a toggle:
```json
{
    "name": "TheNameOfYourBlendShape"
    "type": "toggle",
    "offValue": 0,
    "onValue": 1
}
```

#### Sliders
Sliders require 5 fields, the slider will default to `"minValue"` value and it will only move in multiples of `"step"`.  
`"minValue"` is only the default value, it *can* be smaller than `"maxValue"`.

To add a slider:
```json
{
    "name": "TheNameOfYourBlendShape"
    "type": "slider",
    "step": 0.5,
    "minValue": 0,
    "maxValue": 1
}
```
This example will create a slider that starts at 0, ends at 1, and only accepts the values: 0, 0.5, 1.
