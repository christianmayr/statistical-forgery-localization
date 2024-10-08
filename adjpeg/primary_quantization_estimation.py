import numpy as np
import jpeglib
from utils import zz_index_8x8

DCT_RANGE = 1024


def primary_quantization_estimation(
    img: jpeglib.DCTJPEG,
    dct_coefficient_range: range,
    max_quantization_step=100,
    __DEBUG__=False,
):
    """
    Estimate the first quantization matrix for a double-compressed image.

    Args:
    - img: jpeglib image object
    - dct_coefficient_range: range() of DCT coefficients to be used for the calculation
    - max_quantization_step: highest quantization step value to be considered for the calculation
    - __DEBUG__: increase output

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
    img_spatial_cropped.write_spatial("temp/img_q2.jpeg", qt=img.qt)
    img_q2 = jpeglib.read_dct("temp/img_q2.jpeg")

    q1_result = np.full((8, 8), np.nan)
    l_sum = 0

    for current_coefficient in dct_coefficient_range:
        # get coordinates for the DCT coefficient and the qt step
        x, y = zz_index_8x8(current_coefficient)

        # get DCT coefficient array from the cropped image
        img_0_Y_dct = img_0.Y[:, :, x, y].copy()
        img_q2_Y_dct = img_q2.Y[:, :, x, y].copy()

        # create histogram of single compressed version
        img_q2_Y_dct_histogram, _ = np.histogram(
            img_q2_Y_dct,
            bins=np.arange(-DCT_RANGE, DCT_RANGE + 2) - 0.5,
        )

        # get DCT coefficient array from the original image and calculate the histogram
        img_Y_dct_histogram, _ = np.histogram(
            img.Y[:, :, x, y],
            bins=np.arange(-DCT_RANGE, DCT_RANGE + 2) - 0.5,
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
                bins=np.arange(-DCT_RANGE, DCT_RANGE + 2) - 0.5,
            )

            # TODO: Maybe add gaussean filter to img_c2_Y_dct_histogram to implement R/T error
            # TODO: Make add mixture estimation instead of statically set mixture

            # compare the histogram of the original image to the mixture of estimated histograms
            original_histogram = img_Y_dct_histogram
            estimated_histogram = (
                0.5 * img_c2_Y_dct_histogram + 0.5 * img_q2_Y_dct_histogram
            )
            l = np.sum(np.abs(np.subtract(estimated_histogram, original_histogram)))

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
                print(f"{i-DCT_RANGE}\t{img_Y_dct_histogram[i]}\t{w_histogram[i]}")

    if __DEBUG__:
        print(f"Error Sum: {l_sum}")
        print(q1_result)

    return q1_result
