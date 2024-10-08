import unittest
from adjpeg.adjpeg_localization import adjpeg_localization
import jpeglib


def load_image(image_path) -> jpeglib.DCTJPEG:
    img = jpeglib.read_dct(image_path)
    return img


class BasicOperation(unittest.TestCase):
    def test_runs_without_exception(self):
        img = load_image("./images/sample_image.jpeg")
        adjpeg_localization(img, range(1, 2))
