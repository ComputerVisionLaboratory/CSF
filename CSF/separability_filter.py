# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_separability_filter.ipynb (unless otherwise specified).

__all__ = ['expand_dim_to_3', 'intensity_region_1', 'intensity_region_2', 'seperability_filter', 'conv2d',
           'cvtIntegralImage', 'cvtCombSimpRectFilter', 'tmpFnc']

# Cell
import torch as t
import torch.nn.functional as F

from ball_detection.utils import plot_images

# Cell

def expand_dim_to_3(arr):
    if arr.ndim == 2:
        return np.expand_dims(arr, axis=-1)
    elif arr.ndim == 3:
        return arr
    else:
        raise ValueError()


def intensity_region_1(img, cx, cy, r, return_pixels=False):
    width = img.shape[0]
    height = img.shape[1]
    mask = np.zeros((width, height), np.uint8)

    circle_img = cv.circle(mask,(cx,cy),r, (255,255,255), thickness=-1)
    masked_data = cv.bitwise_and(img, img, mask=circle_img)[cy-r:cy+r+1, cx-r:cx+r+1]

    masked_data = expand_dim_to_3(masked_data)
    pixels = masked_data[masked_data.sum(axis=2)!=0]
    n_pixels = len(pixels)

    if return_pixels:
        return pixels
    return pixels.mean(axis=0).mean(), n_pixels

def intensity_region_2(img, cx, cy, r_in, r_out, return_pixels=False):

    assert r_in < r_out
    width = img.shape[0]
    height = img.shape[1]
    mask_r_out, mask_r_in = np.zeros((width, height), np.uint8), np.zeros((width, height), np.uint8)

    mask_r_out = cv.circle(mask_r_out,(cx,cy),r_out, (255,255,255), thickness=-1)
    mask_r_in = cv.circle(mask_r_in,(cx,cy),r_in, (255,255,255), thickness=-1)
    mask = cv.bitwise_and(mask_r_out, mask_r_out, mask=cv.bitwise_not(mask_r_in))

    masked_data = cv.bitwise_and(img, img, mask=mask)
    masked_data = expand_dim_to_3(masked_data)

    pixels = masked_data[masked_data.sum(axis=2)!=0]
    n_pixels = len(pixels)
    if return_pixels:
        return pixels

    return pixels.mean(axis=0).mean(), n_pixels


def seperability_filter(img, r_in, r_out):
    width, height = img.shape[:2]
    result = np.zeros((width, height))

    for x in tqdm(range(r_out, width-r_out)):
        for y in range(r_out, height-r_out):

            r1_pixels = intensity_region_1(img, x, y, r_in, True)
            r2_pixels = intensity_region_2(img, x, y, r_in, r_out, True)

            r1_mean = r1_pixels.mean(axis=0, keepdims=True).T
            r2_mean = r2_pixels.mean(axis=0, keepdims=True).T

            n_r1 = len(r1_pixels)
            n_r2 = len(r2_pixels)

            n_overall = n_r1 + n_r2
            overall_mean = r1_mean * n_r1/n_overall + r2_mean * n_r2/n_overall

            S_B = n_overall * (r1_mean - overall_mean).dot((r1_mean - overall_mean).T) + \
                n_overall * (r2_mean - overall_mean).dot((r2_mean - overall_mean).T)


            S_T = np.cov(np.concatenate([r1_pixels, r2_pixels]).T)

            if S_B.size==1:
                result[x,y] = S_B / S_T
            else:
                result[x,y] = np.trace(S_B) / np.trace(S_T)

    return result

# Cell
def conv2d(X, W, normalize_weights=True, **kwargs):
    # Do stuff on the input tensor
    X = t.FloatTensor(X)
    if X.ndim==2:
        X = X.view(1, 1, *X.shape)
    elif X.ndim==3:
        X = X.view(1, *X.shape)
    else:
        assert X.ndim==4

    # Do stuff on the weights
    c = X.shape[1]
    W = t.FloatTensor(W)
    h, w = W.shape[-2:]
    W = W.view(1, 1, h, w).repeat(c,1,1,1)
    c = X.shape[1]
    Y = F.conv2d(X, W, groups=c, **kwargs)
    return Y

# Cell
import numpy as np

def cvtIntegralImage(X):
    H, W = X.shape
    Z = np.zeros((H+1, W+1), np.float64)
    Z[1:,1:] = np.cumsum(np.cumsum(X,0),1)
    return Z

def cvtCombSimpRectFilter(I,P,sh):
    bh = sh*2
    bw = np.ceil(sh/3).astype(np.int64)
    sw = np.ceil(sh/3).astype(np.int64)
    dh = 0
    dw = 0

    MAP   = np.zeros((I.shape[0]-1, I.shape[1]-1, 2), np.float64)

    MAP[:,:,0] = tmpFnc(I,P,bh,bw,sh,sw,dh,dw)
    MAP[:,:,1] = tmpFnc(I,P,bw,bh,sw,sh,dh,dw)

    return MAP

def tmpFnc(I,P,bh,bw,sh,sw,dh,dw):
    MAP   = np.zeros((I.shape[0]-1, I.shape[1]-1), np.float64)
    H,W = MAP.shape
    r = np.max([bh,bw])
    N  = (2*bh+1)*(2*bw+1)
    N1 = (2*sh+1)*(2*sw+1)
    N2 = N-N1

    S = (
        I[r -bh  :H-r -bh   ,r -bw  :W-r -bw  ]
      + I[r +bh+1:H-r +bh+1 ,r +bw+1:W-r +bw+1]
      - I[r -bh  :H-r -bh   ,r +bw+1:W-r +bw+1]
      - I[r +bh+1:H-r +bh+1 ,r -bw  :W-r -bw  ]
    )
    T = (
        P[r -bh  :H-r -bh   ,r -bw  :W-r -bw  ]
      + P[r +bh+1:H-r +bh+1 ,r +bw+1:W-r +bw+1]
      - P[r -bh  :H-r -bh   ,r +bw+1:W-r +bw+1]
      - P[r +bh+1:H-r +bh+1 ,r -bw  :W-r -bw  ]
    )
    M = S/N
    Y = T/N
    St = Y - np.power(M, 2)
    S1 = (
         I[r -sh+dh  :H-r -sh+dh   ,r -sw+dw  :W-r -sw+dw]
       + I[r +sh+dh+1:H-r +sh+dh+1,r +sw+dw+1:W-r +sw+dw+1]
       - I[r -sh+dh  :H-r -sh+dh  ,r +sw+dw+1:W-r +sw+dw+1]
       - I[r +sh+dh+1:H-r +sh+dh+1,r -sw+dw  :W-r -sw+dw]
    )
    S2=S-S1
    M1=S1/N1
    M2=S2/N2

    Sb = ((N1*(np.power(M1-M, 2))) + (N2*(np.power(M2-M, 2))))/N
    MAP[r:H-r,r:W-r] = (Sb/St)*np.sign(M2-M1)
    MAP[np.isnan(MAP)]=0
    MAP[np.isinf(MAP)]=0

    return MAP
