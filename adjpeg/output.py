from pathlib import Path
import jpeglib
import numpy as np

PERCENTILE_VALUE = 100


def write_img_output(likelihood_map, path: Path):
    # output image

    assert (
        likelihood_map.max() - likelihood_map.min() != 0
    ), "likelihood map is the same over all values"

    percentile = np.percentile(likelihood_map, PERCENTILE_VALUE)

    likelihood_map_scaled = (
        (likelihood_map - likelihood_map.min())
        * 255
        / (percentile - likelihood_map.min())
    )

    likelihood_map_clipped = np.clip(likelihood_map_scaled, 0, 255)

    block_shape = (8, 8)
    jpeg_block = np.ones(block_shape)

    likelihood_map_expanded = np.kron(likelihood_map_clipped, jpeg_block)
    likelihood_map_image = np.expand_dims(likelihood_map_expanded, axis=-1)

    img_output = jpeglib.from_spatial(likelihood_map_image.astype(np.uint8))
    img_output.height = likelihood_map_image.shape[0]
    img_output.width = likelihood_map_image.shape[1]

    # TODO add path validation
    img_output.write_spatial(str(path))
