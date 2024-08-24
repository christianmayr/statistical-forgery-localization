import argparse
import pathlib
from io import TextIOWrapper
import jpeglib
from collections.abc import Container
from utils import adjpegBanner
from adjpeg_localization import adjpeg_localization


# Utils to have range as a checked argument
def parse_range(value):
    try:
        start, end = map(int, value.split("-"))
        if start >= end:
            raise argparse.ArgumentTypeError(
                f"Start of range ({start}) cannot be greater/equal to end ({end}). See help (-h) page."
            )
        return range(start, end)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid range: '{value}'. Expected format 'start-end'. See help (-h) page."
        )


class RangeContainer(Container):
    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def __contains__(self, other: range):
        return self.start <= other.start and self.stop >= other.stop

    def __iter__(self):
        self.iter = True
        return self

    def __next__(self):
        if self.iter == False:
            raise StopIteration
        else:
            self.iter = False
            return self

    def __repr__(self):
        return f"RangeContainer({self.start}, {self.stop})"


if __name__ == "__main__":
    # Initialize
    parser = argparse.ArgumentParser()

    a = range(0, 10)
    a.__contains__

    # Add arguments
    parser.add_argument(
        "image_path", type=str, help="input image file path in JPEG format"
    )
    parser.add_argument(
        "--dct-range",
        "-r",
        type=parse_range,
        choices=RangeContainer(1, 64),
        default=range(1, 12),
        metavar="range",
        help="integer range of zero-indexed DCT coefficients between 0 and 63 to be analysed. write as two integers with '-' in between. in 'a-b' the first coefficient is 'a' and the last coefficient is 'b-1' (like the python range() method)",
    )

    # TODO: add quiet argument
    # TODO: add output path/file
    # TODO: add DCT range argument

    # Run program
    args = parser.parse_args()
    image_path: str = args.image_path
    dct_coefficient_range: range = args.dct_range

    try:
        img = jpeglib.read_dct(image_path)
    except FileNotFoundError as e:
        print(e)
        exit(e.errno)

    print(
        f"{adjpegBanner}\nStarting statistical ADJPEG manipulation localization with parameters \
        \n\tImage: {image_path} \
        \n\tFirst DCT Coefficient: {dct_coefficient_range.start} \
        \n\tLast DCT Coefficient: {dct_coefficient_range.stop-1}"
    )

    try:
        adjpeg_localization(img, dct_coefficient_range)
    except ValueError as e:
        print(e)
        exit(1)
