import numpy as np
import matplotlib.pyplot as plt
import jpeglib
from jpeglib import DCTJPEG
from utils import zz_index_8x8
from primary_quantization_estimation import primary_quantization_estimation
from math import floor, ceil

P0_SHIFT = 1


def estimate_unquantized_DCT(img: DCTJPEG) -> DCTJPEG:
    """
    Calculates estimated unquantized DCT coefficients

    Args:
    - img: DCTJPEG image object

    Returns: DCTJPEG image object
    """
    # Create shifted version to sample from
    img.write_dct("temp/temp.jpeg")
    img_spatial = jpeglib.read_spatial("temp/temp.jpeg")

    shifted_spatial = np.roll(img_spatial.spatial, P0_SHIFT, axis=[0, 1])
    img_spatial_cropped = img_spatial
    img_spatial_cropped.spatial = shifted_spatial

    # Create img_0 (DCT coefficients sampled without compression)
    img_spatial_cropped.write_spatial("temp/img_0_shift.jpeg", qt=100)
    img_0 = jpeglib.read_dct("temp/img_0_shift.jpeg")

    return img_0


def probability_single_compressed(value, unquantized_distribution):
    pass


def probability_double_compressed(value, q1, unquantized_distribution):
    pass


def periodic_dq_function(value, q1: int, q2: int):
    MU = 0  # TODO required if DC DCT coefficient is used
    l = q1 * (ceil(q2 / q1 * (value - MU / q2 - 0.5)) - 0.5)
    r = q1 * (floor(q2 / q1 * (value - MU / q2 + 0.5)) + 0.5)

    result = (r - l) / q2
    assert result > 0, "output of periodic function has to be positive"

    return result


def adjpeg_localization(img: DCTJPEG, dct_coefficient_range: range, quiet=False):
    """
    Localize and detect manipulations in double compressed images. Uses single-compression forgery hypothesis.

    Args:
    - img: DCTJPEG image object

    Returns: likelyhood map
    """
    # assure JPEG image has 64 coefficients per block
    assert (
        np.prod(img.Y.shape[2:]) == 64
    ), "Number of DCT coefficients per block has to be 64"

    if not quiet:
        print("\nEstimating primary quantization step")
    Q1 = primary_quantization_estimation(img, dct_coefficient_range)
    Q2 = img.qt[0]

    if not quiet:
        print("Estimating unquantized DCT coefficient")
    img0 = estimate_unquantized_DCT(img)

    # likelyhood map does not yet fulfill SCF hypothesis
    likelyhood_map = np.full(img.Y.shape[:2], 1, dtype=float)

    if not quiet:
        print("Starting likelyhood map calculation")
    for current_coefficient in dct_coefficient_range:
        if not quiet:
            print(f"\tCurrent DCT coefficient: {current_coefficient}")

        # get coordinates for the DCT coefficient and the qt step
        x, y = zz_index_8x8(current_coefficient)

        img_Y_dct = img.Y[:, :, x, y].copy()

        for x in range(img_Y_dct.shape[0]):
            for y in range(img_Y_dct.shape[1]):
                pass

        probability_single_compressed = None
        probability_double_compressed = None

        # likelyhood_map *= probability_double_compressed / probability_single_compressed

    # output image
    if not quiet:
        print("Writing likelyhood map to output/output.jpeg")

    likelyhood_min = np.min(likelyhood_map)
    likelyhood_max = np.max(likelyhood_map)

    assert (
        likelyhood_max - likelyhood_min != 0
    ), "Likelyhood map is the same over all values"

    likelyhood_map_scaled = (
        (likelyhood_map - likelyhood_min) * 255 / (likelyhood_max - likelyhood_min)
    )

    block_shape = (8, 8)
    jpeg_block = np.ones(block_shape)

    likelyhood_map_expanded = np.kron(likelyhood_map_scaled, jpeg_block)
    likelyhood_map_image = np.expand_dims(likelyhood_map_expanded, axis=-1)

    img_output = jpeglib.from_spatial(likelyhood_map_image.astype(np.uint8))
    img_output.height = img.Y.shape[0] * block_shape[0]
    img_output.width = img.Y.shape[1] * block_shape[1]

    img_output.write_spatial("output/output.jpeg")

    return likelyhood_map
