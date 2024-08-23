import numpy
import unittest
from adjpeg.utils import zz_index_8x8


class Utils(unittest.TestCase):
    def test_zz_index_8x8(self):
        test = numpy.full((8, 8), numpy.nan)
        for i in range(64):
            test[zz_index_8x8(i)] = i

        ref = numpy.array(
            [
                [0, 1, 5, 6, 14, 15, 27, 28],
                [2, 4, 7, 13, 16, 26, 29, 42],
                [3, 8, 12, 17, 25, 30, 41, 43],
                [9, 11, 18, 24, 31, 40, 44, 53],
                [10, 19, 23, 32, 39, 45, 52, 54],
                [20, 22, 33, 38, 46, 51, 55, 60],
                [21, 34, 37, 47, 50, 56, 59, 61],
                [35, 36, 48, 49, 57, 58, 62, 63],
            ]
        )

        numpy.testing.assert_array_equal(test, ref)
