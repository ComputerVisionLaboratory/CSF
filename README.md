# Circular Separability Filter
> Circle detection in images using Python.


## Installation

```bash
pip install circle_finder # doesn't work yet
```

or using github
```bash
git clone https://github.com/ComputerVisionLaboratory/circle_finder
cd circle_finder
pip install -e .
```


## Documentation

[https://computervisionlaboratory.github.io/circle_finder/](https://computervisionlaboratory.github.io/circle_finder/)

## Usage

```python
import cv2 as cv
from circle_finder.core import EllipitcalSeparabilityFilter


img = cv.imread('/path/to/image.jpg')
esf = EllipitcalSeparabilityFilter()

circles = esf.find_circles(img, num_circles=1)
print(circles)
> >>[[50, 50]]
```


See more in [online documentation](https://computervisionlaboratory.github.io/circle_finder/).

## Roadmap

### Implement differential separability filter

For deep learning based approach

## Release Notes

###  (~pre-release)
* 2021/09/10 - Addded EllipticalSeparabilityFilter
* 2021/09/20 - Added torch convolutions for faster filtering
