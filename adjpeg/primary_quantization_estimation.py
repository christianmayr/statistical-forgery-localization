import numpy as np
import matplotlib.pyplot as plt
import jpeglib
from jpeglib import DCTJPEG
from utils import zz_index_8x8


def primary_quantization_estimation(
    img: jpeglib.DCTJPEG,
    dct_coefficient_range: range,
    max_dct_abs_value: int = 15,
    max_quantization_step=100,
    __DEBUG__=False,
):
    """
    Estimate the first quantization matrix for a double-compressed image.

    Args:
    - img: jpeglib image object

    Returns: Quantization matrix
    """

    # assure JPEG image has 64 coefficients per block
    assert (
        np.prod(img.Y.shape[2:]) == 64
    ), "Number of DCT coefficients per block has to be 64"

    # Create cropped version to sample from
    img.write_dct("temp/temp.jpeg")
    img_spatial = jpeglib.read_spatial("temp/temp.jpeg")

    shape_spatial = img_spatial.spatial.shape
    assert (
        shape_spatial[0] > 16 and shape_spatial[1] > 16
    ), "Image is too small to be cropped and re-compressed"

    cropped_spatial = img_spatial.spatial[
        4 : shape_spatial[0] - 4, 4 : shape_spatial[1] - 4, :
    ]
    img_spatial_cropped = img_spatial
    img_spatial_cropped.spatial = cropped_spatial
    img_spatial_cropped.width -= 8
    img_spatial_cropped.height -= 8

    # Create img_0 (DCT coefficients sampled without compression)
    img_spatial_cropped.write_spatial("temp/img_0.jpeg", qt=100)
    img_0 = jpeglib.read_dct("temp/img_0.jpeg")

    # Create img_q2 (DCT coefficients sampled with only second compression)
    # img_spatial_cropped.write_spatial("img_q2.jpeg", qt=img.qt)
    # img_q2 = jpeglib.read_dct("img_q2.jpeg")

    q1_result = np.full((8, 8), np.nan)
    l_sum = 0

    # TODO: Add expectation maximization

    for current_coefficient in dct_coefficient_range:
        # get coordinates for the DCT coefficient and the qt step
        x, y = zz_index_8x8(current_coefficient)

        # get DCT coefficient array from the cropped image
        img_0_Y_dct = img_0.Y[:, :, x, y].copy()
        img_0_Y_dct.sort()

        # get DCT coefficient array from the original image and calculate the histogram
        img_Y_dct_histogram, _ = np.histogram(
            img.Y[:, :, x, y],
            bins=np.arange(-max_dct_abs_value, max_dct_abs_value + 2) - 0.5,
        )

        # get quantization step of the qt in the original image for the corresponding current_coefficient
        q2: int = img.qt[0][zz_index_8x8(current_coefficient)]

        l_max = np.inf
        for q1 in range(1, max_quantization_step + 1):

            ##### First quantization step #####
            # DCT coefficients in img_0 are quantized with value 1
            # Hence no multiplication needs to be performed to dequantize the coefficients
            img_c1_Y_dct: list[int] = np.round(np.divide(img_0_Y_dct, q1))
            img_c1_Y_dct *= q1
            # the result is dequantized DCT coefficients

            ##### Second quantization step #####
            img_c2_Y_dct: list[int] = np.round(np.divide(img_c1_Y_dct, q2))
            # the result is quantized DCT coefficients

            # calculate the histogram of the double quantized coefficients
            img_c2_Y_dct_histogram, _ = np.histogram(
                img_c2_Y_dct,
                bins=np.arange(-max_dct_abs_value, max_dct_abs_value + 2) - 0.5,
            )

            # TODO: Maybe add gaussean filter to img_c2_Y_dct_histogram to implement R/T error

            # compare to the histogram of the original image
            l = np.sum(np.abs(np.subtract(img_c2_Y_dct_histogram, img_Y_dct_histogram)))

            if l < l_max:
                l_max = l
                q1_result[zz_index_8x8(current_coefficient)] = q1
                w_histogram = img_c2_Y_dct_histogram

        l_sum += l_max
        if __DEBUG__:
            print(
                f"DCT_coefficient: {current_coefficient}; (x,y): ({x},{y}); Q1: {q1_result[zz_index_8x8(current_coefficient)]}; L: {l_max}"
            )
            print("index\timg\tapprox")
            for i in range(len(w_histogram)):
                print(
                    f"{i-max_dct_abs_value}\t{img_Y_dct_histogram[i]}\t{w_histogram[i]}"
                )

    if __DEBUG__:
        print(f"Error Sum: {l_sum}")

    return q1_result
