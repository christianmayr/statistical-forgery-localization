import numpy as np
import matplotlib.pyplot as plt
import jpeglib
from jpeglib import DCTJPEG
from adjpeg import utils


def adjpeg_localization(img: jpeglib.DCTJPEG, dct_coefficient_range: range):
    # assure JPEG image has 64 coefficients per block
    assert (
        np.prod(img.Y.shape[2:]) == 64
    ), "Number of DCT coefficients per block has to be 64"

    likelyhood_map = np.full(img.Y.shape[:2], 1, dtype=float)

    for current_coefficient in dct_coefficient_range:
        # get coordinates for the DCT coefficient and the qt step
        x, y = utils.zz_index_8x8(current_coefficient)

        img_Y_dct = img.Y[:, :, x, y]

    # output image
    block_shape = (8, 8)
    jpeg_block = np.ones(block_shape)

    likelyhood_map_expanded = np.kron(likelyhood_map, jpeg_block)
    likelyhood_map_image = np.round(
        np.expand_dims(likelyhood_map_expanded, axis=-1) * 255
    ).astype(np.uint8)

    img_output = jpeglib.from_spatial(likelyhood_map_image)
    img_output.height = img.Y.shape[0] * block_shape[0]
    img_output.width = img.Y.shape[1] * block_shape[1]

    img_output.write_spatial("output/output.jpeg")
    print(likelyhood_map.shape)
    print(likelyhood_map_expanded.shape)

    return likelyhood_map
