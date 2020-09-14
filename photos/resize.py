import argparse
import fractions
import glob
import os
import pathlib
import re
import subprocess

from PIL import Image


class AspectRatio(object):
    def __init__(self, aspect_ratio):
        parts = aspect_ratio.split(':')
        if len(parts) != 2:
            raise Exception(f'{aspect_ratio} is not a valid aspect ratio -- expected format: width:height')

        width, height = parts
        self.aspect_ratio = fractions.Fraction(int(width), int(height))

    def get_new_dimensions(self, width, height):
        original_aspect_ratio = fractions.Fraction(width, height)
        if original_aspect_ratio >= self.aspect_ratio:
            return width, int(width * 1 / self.aspect_ratio)
        else:
            return int(height * self.aspect_ratio), height


def resize_image(image, args):
    aspect_ratio = AspectRatio(args.aspect_ratio)
    old_width, old_height = image.size

    if args.output_dir:
        new_image = f'{args.output_dir}/{os.path.basename(image.filename)}'
    else:
        new_image = re.sub('\\.JPG', '_resized.JPG', image.filename)

    new_width, new_height = aspect_ratio.get_new_dimensions(old_width, old_height)
    scale = min(new_width / old_width, new_height / old_height)
    width_padding = f'({new_width}-{old_width})/2'
    height_padding = f'({new_height}-{old_height})/2'

    subprocess.run([
        'ffmpeg',
        '-i',
        image.filename,
        '-q:v',
        '1',
        '-vf',
        f'scale=iw*{scale}:ih*{scale},'
        f'pad={new_width}:{new_height}:{width_padding}:{height_padding}:color={args.color},'
        'format=rgb24',
        new_image
    ])


def parse_args():
    parser = argparse.ArgumentParser()
    home = pathlib.Path.home()

    parser.add_argument('dir', type=str)
    parser.add_argument('aspect_ratio', type=str)
    parser.add_argument('--filter_files', type=str, default='*.JPG')
    parser.add_argument('--filter_width', type=int)
    parser.add_argument('--filter_height', type=int)
    parser.add_argument('--filter_portrait', dest='filter_portrait', action='store_true')
    parser.add_argument('--filter_landscape', dest='filter_landscape', action='store_true')
    parser.add_argument('--color', type=str, choices=['white', 'black'], default='white')
    parser.add_argument('--output_dir', type=str, default=str(home / 'Google Drive' / 'Photos' / 'Output'))

    return parser.parse_args()


def get_images(args):
    image_files = glob.glob(f'{os.path.abspath(args.dir)}/{args.filter_files}')

    for image_file in image_files:
        image = Image.open(os.path.abspath(image_file))

        if args.filter_width and image.width != args.filter_width:
            continue
        elif args.filter_height and image.height != args.filter_height:
            continue
        elif args.filter_portrait and image.width >= image.height:
            continue
        elif args.filter_landscape and image.width <= image.height:
            continue

        yield image


def run():
    args = parse_args()

    if args.output_dir and not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    for image in get_images(args):
        resize_image(image, args)


if __name__ == '__main__':
    run()
