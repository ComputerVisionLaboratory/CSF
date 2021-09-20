# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = ['expand_dim_to_3', 'parametric_ellipse', 'elliplise', 'EllipticalSeparabilityFilter']

# Cell
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import torch
from torchvision.transforms import ToTensor
from skimage.feature import peak_local_max

# Cell

#export
def expand_dim_to_3(arr):
    if arr.ndim == 2:
        return np.expand_dims(arr, axis=-1)
    elif arr.ndim == 3:
        return arr
    else:
        raise ValueError()

def parametric_ellipse(alpha, A, a, b):
    X = a * np.cos(alpha) * np.cos(A) - b * np.sin(alpha) * np.sin(A)
    Y = a * np.cos(alpha) * np.sin(A) + b * np.sin(alpha) * np.cos(A)
    return X, Y

def elliplise(axes, angle, center=None, width=None, height=None):
    a = axes[0]
    b = axes[1]

    A = np.deg2rad(angle)
    cc = [parametric_ellipse(alpha, A, a, b) for alpha in np.linspace(0, np.pi*2, 1000)]

    if height is None and width is None:
        width, height = np.max(cc, axis=0)
        width = round(width) * 2 + 1
        height = round(height) * 2 + 1

    if center is None:
        center = (round(width/2), round(height/2))

    mask = np.zeros((height, width), np.uint8)
    template = torch.Tensor(cv.ellipse(mask, center, axes, angle, color=1, thickness=-1, startAngle=0, endAngle=360)).unsqueeze(0)
    return template


# Cell

class EllipticalSeparabilityFilter:
    def __init__(self, axes_in, axes_out, angle):
        self.axes_in = axes_in
        self.axes_out = axes_out
        self.angle = angle

        inner_region, outer_region, full_region = self.ellipse_templates()
        self.inner_region = inner_region
        self.outer_region = outer_region
        self.full_region = full_region

    def __call__(self, img):
        axes_in, axes_out, angle = self.axes_in, self.axes_out, self.angle
        inner_region, outer_region, full_region = self.inner_region, self.outer_region, self.full_region

        top = bottom = axes_out[0]
        right = left = axes_out[1]
        borderType = cv.BORDER_REPLICATE
        img = cv.copyMakeBorder(img, top, bottom, left, right, borderType)

        img = ToTensor()(img)
        c = img.shape[0]
        img = img.unsqueeze(0)

        n_inner = inner_region.sum()
        n_outer = outer_region.sum()
        n_full = n_inner + n_outer

        w_inner = inner_region.repeat([c,1,1,1]) / n_inner
        w_outer = outer_region.repeat([c,1,1,1]) / n_outer
        w_full = full_region.repeat([c,1,1,1]) / n_full

        m_inner = torch.nn.functional.conv2d(img, w_inner, groups=c)[0]
        m_outer = torch.nn.functional.conv2d(img, w_outer, groups=c)[0]
        m_full = torch.nn.functional.conv2d(img, w_full, groups=c)[0]

        sb_map = n_inner * (m_inner - m_full)**2 + n_outer * (m_outer - m_full)**2

        unfolded = torch.nn.functional.unfold(img.permute((1,0,2,3)), w_full.shape[-2:])
        meansubbed = unfolded - m_full.reshape(c, 1, -1)
        squared = meansubbed ** 2
        st_map = (w_full.reshape(c, 1, -1) @ squared).reshape(sb_map.shape[-3:])

        out = sb_map / st_map
        return out.mean(axis=0, keepdim=True)

    def ellipse_templates(self):
        axes_in, axes_out, angle = self.axes_in, self.axes_out, self.angle
        full_region = elliplise(axes_out, angle)

        height, width = full_region.shape[1:]
        inner_region = elliplise(axes=axes_in, angle=angle, height=height, width=width)

        outer_region = full_region - inner_region

        return inner_region, outer_region, full_region

    def find_circles(self, img, num_circles=None):
        sepmap = self.__call__(img).numpy().squeeze().T
        sepmap[np.isnan(sepmap)]=0
        peaks = peak_local_max(sepmap)

        if num_circles is None:
            return peaks
        else:
            return peaks[:num_circles]
