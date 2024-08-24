from pathlib import Path
import jpeglib
import numpy as np

PERCENTILE_VALUE = 60


def write_img_output(likelyhood_map, path: Path):
    # output image

    assert (
        likelyhood_map.max() - likelyhood_map.min() != 0
    ), "Likelyhood map is the same over all values"

    percentile = np.percentile(likelyhood_map, PERCENTILE_VALUE)

    likelyhood_map_scaled = (
        (likelyhood_map - likelyhood_map.min())
        * 255
        / (percentile - likelyhood_map.min())
    )

    likelyhood_map_clipped = np.clip(likelyhood_map_scaled, 0, 255)

    block_shape = (8, 8)
    jpeg_block = np.ones(block_shape)

    likelyhood_map_expanded = np.kron(likelyhood_map_clipped, jpeg_block)
    likelyhood_map_image = np.expand_dims(likelyhood_map_expanded, axis=-1)

    img_output = jpeglib.from_spatial(likelyhood_map_image.astype(np.uint8))
    img_output.height = likelyhood_map_image.shape[0]
    img_output.width = likelyhood_map_image.shape[1]

    # TODO add path validation
    img_output.write_spatial(str(path))
