from cProfile import Profile
from pstats import SortKey, Stats
import unittest
from adjpeg import primary_compression_estimation as pce
import jpeglib
import numpy.testing


def load_image(image_path) -> jpeglib.DCTJPEG:
    img = jpeglib.read_dct(image_path)
    return img


class Benchmark(unittest.TestCase):
    def test_benchmark(self):
        img = load_image("./images/0_DC_50_0_80_0.jpeg")

        with Profile() as profile:
            result = pce.primary_quantization_estimation(
                img, range(0, 15), max_dct_abs_value=15
            )
            print(f"\nOutput\n{result}")
            (Stats(profile).strip_dirs().sort_stats(SortKey.TIME).print_stats())


class BasicOperation(unittest.TestCase):
    def test_runs_without_exception(self):
        img = load_image("./images/double_compressed.jpg")
        result = pce.primary_quantization_estimation(
            img, range(0, 10), max_dct_abs_value=15, __DEBUG__=True
        )
        print(f"\nOutput\n{result}")

    def test_with_QF_75_80(self):
        img = load_image("./images/0_DC_75_0_80_0.jpeg")
        result = pce.primary_quantization_estimation(
            img, range(0, 10), max_dct_abs_value=15, __DEBUG__=True
        )
        print(f"\nOutput\n{result}")

    def test_with_QF_50_80(self):
        img = load_image("./images/0_DC_50_0_80_0.jpeg")
        result = pce.primary_quantization_estimation(
            img, range(0, 32), max_dct_abs_value=15, __DEBUG__=True
        )

        ref = numpy.array(
            [
                [16, 11, 10, 16, 24, 40, 51, 61],
                [12, 12, 14, 19, 26, 58, 60, 55],
                [14, 13, 16, 24, 40, 57, 69, 56],
                [14, 17, 22, 29, 51, 87, 80, 62],
                [18, 22, 37, 56, 68, 109, 103, 77],
                [24, 35, 55, 64, 81, 104, 113, 92],
                [49, 64, 78, 87, 103, 121, 120, 101],
                [72, 92, 95, 98, 112, 100, 103, 99],
            ]
        )

        print(f"\nOutput\n{result}")

        comparison_func = numpy.vectorize(
            lambda x, y: numpy.nan if x == numpy.nan else x - y
        )

        correctness = comparison_func(result, ref)

        print(f"\nCorrectness\n{correctness}")
