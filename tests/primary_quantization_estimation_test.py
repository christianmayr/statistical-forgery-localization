from cProfile import Profile
from pstats import SortKey, Stats
import unittest
from adjpeg.primary_quantization_estimation import primary_quantization_estimation
import jpeglib
import numpy.testing


def load_image(image_path) -> jpeglib.DCTJPEG:
    img = jpeglib.read_dct(image_path)
    return img


class Benchmark(unittest.TestCase):
    def test_benchmark(self):
        img = load_image("./images/0_DC_50_0_80_0.jpeg")

        with Profile() as profile:
            result = primary_quantization_estimation(img, range(0, 15))
            print(f"\nOutput\n{result}")
            (Stats(profile).strip_dirs().sort_stats(SortKey.TIME).print_stats())


class BasicOperation(unittest.TestCase):
    def test_runs_without_exception(self):
        img = load_image("./images/sample_image.jpeg")
        result = primary_quantization_estimation(
            img,
            range(0, 20),
            max_quantization_step=20,
            __DEBUG__=True,
        )
