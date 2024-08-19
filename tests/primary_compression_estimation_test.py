from cProfile import Profile
from pstats import SortKey, Stats
import unittest
from adjpeg import primary_compression_estimation as pce
import jpeglib
import numpy.testing

def load_image() -> jpeglib.DCTJPEG:
    img = jpeglib.read_dct("./images/0_DC_50_0_80_0.jpeg")
    return img

class Benchmark(unittest.TestCase):
    def test_benchmark(self):
        img = load_image()
        
        with Profile() as profile:
            result = pce.pce(img, range(0,15), max_dct_abs_value=15)
            print(f"\nOutput\n{result}")
            (
                Stats(profile)
                .strip_dirs()
                .sort_stats(SortKey.TIME)
                .print_stats()
            )  

class BasicOperation(unittest.TestCase):
    def test_runs_without_exception(self):
        img = load_image()
        result = pce.pce(img, range(25,30), max_dct_abs_value=15, __DEBUG__ = True)
        print(f"\nOutput\n{result}")
        
        
        
class Utils(unittest.TestCase):
    def test_zz_index_8x8(self):
        test = numpy.full((8,8), numpy.nan)
        for i in range(64):
            test[pce.zz_index_8x8(i)]=i
        
        ref = numpy.array([
            [ 0,  1,  5,  6, 14, 15, 27, 28],
            [ 2,  4,  7, 13, 16, 26, 29, 42],
            [ 3,  8, 12, 17, 25, 30, 41, 43],
            [ 9, 11, 18, 24, 31, 40, 44, 53],
            [10, 19, 23, 32, 39, 45, 52, 54],
            [20, 22, 33, 38, 46, 51, 55, 60],
            [21, 34, 37, 47, 50, 56, 59, 61],
            [35, 36, 48, 49, 57, 58, 62, 63]
            ])
        
        numpy.testing.assert_array_equal(test, ref)