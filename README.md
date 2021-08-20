# Circular Separability Filter
> Circle detection in images using Python.


## Installation

```bash
pip install CSF
```

or using github
```bash
git clone https://github.com/ComputerVisionLaboratory/CSF
cd CSF
pip install .
```


## Usage

```python
import cv2 as cv
import circle_finder


img = cv.imread('/path/to/image.jpg')
csf = circle_finder.CircularSeparabilityFilter()

circles = csf(img)
print(circles)
```

See more in tutorials.
