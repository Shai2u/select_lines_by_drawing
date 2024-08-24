# Select Lines By Drawing

## Plugin Description:

The Plugin for QGIS empowers users with an intuitive tool for selecting features based on their spatial relationships. This plugin enables users to draw a line on the map canvas, and it automatically selects all feature lines that intersect with the drawn line, and removes from the selection lines that do not intersect with the other drawn lines.

Screenshot:

### Automaitc mode (or Simple mode)

![Image](media/automatic_mode.png)
Automatic mode is the simple mode of the plugin. It allows users to draw up to 25 lines on the canvas. The first line selects the features (or appends to the existing selection), while subsequent lines filter the selection from the remaining features. This mode streamlines the process of refining feature selection and filtering directly on the canvas.

### Manual mode (or Advance mode)

![Image](media/manual_mode.png)
Manual mode is the Advanced mode of the plugin. It allows users to control the sequence of selection operations. In this mode, users can choose to add to, remove from, or filter the current selection at each step. The plugin executes these operations in the specified order. The drawn lines are color-coded for clarity: green lines add to the current selection, black lines remove from it, and blue lines filter the selection. This mode provides greater flexibility and precision in managing feature selections.
