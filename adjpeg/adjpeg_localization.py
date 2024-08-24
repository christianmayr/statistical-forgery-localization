import numpy as np
import matplotlib.pyplot as plt
import jpeglib
from jpeglib import DCTJPEG
from utils import zz_index_8x8
from primary_quantization_estimation import primary_quantization_estimation
from math import floor, ceil

P0_SHIFT = 1
DCT_RANGE = 1024
DCT_COEFFICIENTS_PER_BLOCK = 64


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


def probability_single_compressed(value: int, q2: int, p0):
    lower_bound = round(q2 * value - q2 / 2)
    if lower_bound < -DCT_RANGE:
        raise ValueError(
            f"Error: Lower bound {lower_bound} in pNDQ function is lower than DCT range {-DCT_RANGE}. Set a higher DCT range!"
        )

    upper_bound = round(q2 * value + q2 / 2)
    if upper_bound > DCT_RANGE:
        raise ValueError(
            f"Error: Upper bound {upper_bound} in pNDQ function is higher than DCT range {DCT_RANGE}. Set a higher DCT range!"
        )

    result: float = 0
    for i in range(lower_bound, upper_bound + 1):
        result += p0[i + DCT_RANGE]

    return result


def periodic_dq_function(value, q1: int, q2: int):
    MU = 0  # TODO required if DC DCT coefficient is used
    l = q1 * (ceil(q2 / q1 * (value - MU / q2 - 0.5)) - 0.5)
    r = q1 * (floor(q2 / q1 * (value - MU / q2 + 0.5)) + 0.5)

    result = (r - l) / q2

    return result if result > 0 else 1


def adjpeg_localization(
    img: DCTJPEG, dct_coefficient_range: range, quiet=False, __DEBUG__=False
):
    """
    Localize and detect manipulations in double compressed images. Uses single-compression forgery hypothesis.

    Args:
    - img: DCTJPEG image object
    - dct_coefficient_range: range() of DCT coefficients to be used for the calculation
    - quiet: reduce output
    - __DEBUG__: increase output

    Returns: likelyhood map
    """
    # assure JPEG image has 64 coefficients per block
    assert (
        np.prod(img.Y.shape[2:]) == 64
    ), "Number of DCT coefficients per block has to be 64"

    if not quiet:
        print("\nEstimating primary quantization step")
    Q1 = primary_quantization_estimation(
        img, dct_coefficient_range, __DEBUG__=__DEBUG__
    )
    Q2 = img.qt[0]

    if not quiet:
        print("Estimating unquantized DCT coefficients")
    img0 = estimate_unquantized_DCT(img)

    # likelyhood map does not yet fulfill SCF hypothesis
    likelyhood_map = np.full(img.Y.shape[:2], 1, dtype=float)

    # set image block height and width for quick reference:
    block_width = img.width_in_blocks(0)
    block_height = img.height_in_blocks(0)

    if not quiet:
        print("Starting likelyhood map calculation")
    for current_coefficient in dct_coefficient_range:
        if not quiet:
            print(f"\tCurrent DCT coefficient: {current_coefficient}")

        # get coordinates for the DCT coefficient and the qt step
        x, y = zz_index_8x8(current_coefficient)
        current_q1 = Q1[x, y]
        current_q2 = Q2[x, y]

        # calculate probability distribution of coefficient values
        img0_Y_dct_histogram, _ = np.histogram(
            img0.Y[:, :, x, y],
            bins=np.arange(-DCT_RANGE, DCT_RANGE + 2) - 0.5,
        )
        p0 = (img0_Y_dct_histogram + 1) / (
            block_width * block_height + (-DCT_RANGE + 2 - DCT_RANGE)
        )

        # create working arrays
        img_Y_dct = img.Y[:, :, x, y].copy()
        if np.all(img_Y_dct == 0):
            raise ValueError(
                f"Error: DCT coefficient {current_coefficient} is zero in the entire image. Choose a different range of DCT coefficients!"
            )
        probability_H0 = np.zeros((block_height, block_width), dtype=float)
        probability_H1 = np.zeros((block_height, block_width), dtype=float)

        for x_block in range(block_width):
            for y_block in range(block_height):
                value = img_Y_dct[y_block, x_block]

                p_H0 = probability_single_compressed(value, current_q2, p0)

                probability_H0[y_block, x_block] = p_H0
                probability_H1[y_block, x_block] = p_H0 * periodic_dq_function(
                    value, current_q1, current_q2
                )

        likelyhood_map *= probability_H0 / probability_H1

    return likelyhood_map
