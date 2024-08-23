import argparse
import pathlib
from io import TextIOWrapper
import jpeglib
import adjpeg

if __name__ == "__main__":
    # Initialize
    parser = argparse.ArgumentParser()

    # Add arguments
    def parse_range(value):
        try:
            start, end = map(int, value.split("-"))
            if start > end:
                raise argparse.ArgumentTypeError(
                    f"Start of range ({start}) cannot be greater than end ({end})."
                )
            return range(start, end + 1)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid range: '{value}'. Expected format 'start-end'."
            )

    parser.add_argument("image_path", type=str, help="Input image in JPEG format")
    parser.add_argument(
        "--dct-range",
        "-r",
        type=parse_range,
        default=range(1, 12),
        help="Integer range start-end of DCT coefficients to be analysed",
    )

    # Run program
    args = parser.parse_args()
    image_path = args.image_path
    dct_coefficient_range = args.dct_range

    try:
        img = jpeglib.read_dct(image_path)
    except FileNotFoundError as e:
        print(e)
        exit(e.errno)

    adjpeg.adjpeg_localization(img, dct_coefficient_range)
