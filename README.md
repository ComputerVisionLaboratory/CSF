# Circular Separability Filter
> Circle detection in images using Python.


![](nbs/sep_demo.gif)

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

circles = csf.find_circles(img, num_circles=1)
print(circles)
>>>[[50, 50]]
```


See more in tutorials.
