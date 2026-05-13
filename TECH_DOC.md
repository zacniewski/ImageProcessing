# Technical Documentation: Image Processing Implementation [Legacy]

> **Note:** This document describes a **legacy system** maintained for historical/educational purposes.

This document provides a deeper dive into the technical implementation of the Image Processing System.

## Image Format Conversion
The application uses both **Qt (PyQt4)** for UI/display and **PIL (Pillow)** for mathematical transformations. This requires frequent conversion between formats.

### Qt to PIL Conversion
Converting a `QImage` to a PIL `Image` involves using a buffer and `cStringIO`:

```python
def image2PIL(self):
    self.bufor = QtCore.QBuffer()
    self.bufor.open(QtCore.QIODevice.ReadWrite)
    self.image.save(self.bufor, "PNG")
    strio = cStringIO.StringIO()
    strio.write(self.bufor.data())
    strio.seek(0)
    self.pil_image = Image.open(strio)
```

### PIL to Qt Conversion
Converting back to `QImage` is done via the `tostring()` method (note: in modern Pillow this is `tobytes()`):

```python
def PIL2qpixmap(self, pil_image):
    data = pil_image.tostring()
    self.PIL2qpixmap_image = QtGui.QImage(
        data, 
        pil_image.size[0], 
        pil_image.size[1], 
        QtGui.QImage.Format_Indexed8
    )
```

## Algorithms

### 1. Brightness Adjustment
The brightness is adjusted using a linear transformation on each pixel $p$:
$$p' = \text{clamp}(p + \text{offset}, 0, 255)$$
In the code, this is implemented using the PIL `point` function:
```python
self.transformed_image = self.pil_image.point(lambda i: i + self.sld.value())
```

### 2. Histogram Generation
The histogram is calculated for grayscale (mode "L") images. 
- **Bin count:** 256 (one for each intensity level).
- **Visualization:** A 256x120 pixel image where each vertical line's height represents the frequency of that intensity.

| Step | Action |
| :--- | :--- |
| 1 | Extract histogram data using `pil_image.histogram()`. |
| 2 | Find the maximum frequency for scaling. |
| 3 | Iterate through bins (0-255) and draw lines using `ImageDraw`. |

## UI Layout
The interface is organized using nested layouts:
- `QVBoxLayout` (Main container)
  - `QHBoxLayout` (Toolbar/Menu)
  - `QHBoxLayout` (Image Headers)
  - `QHBoxLayout` (Main Images)
  - `QVBoxLayout` (Slider Header)
  - `QHBoxLayout` (Slider & LCD)
  - `QHBoxLayout` (Histogram Headers)
  - `QHBoxLayout` (Histogram Displays)
  - `QStatusBar` (Status & Dimensions)
