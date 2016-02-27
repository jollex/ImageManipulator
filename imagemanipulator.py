#!/usr/bin/env python

import argparse, sys, os, random, io
from shutil import copyfile
from PIL import Image
import images2gif

class ImageManipulator(object):
    """ Class for manipulating an Image """
    def __init__(self, image_path):
        self.image = Image.open(image_path)

    def rotate_sections(self, box_size, rotate_options):
        """
        Cuts the image into sections of side length box_size and rotates each
        one using a randomly selected rotation from rotate_options.

        box_size -- The length of each side of each box.
        rotate_options -- A list of length at least one where each member are
        is one of: None, Image.ROTATE_90, Image.ROTATE_180, or Image.ROTATE_270
        """
        n_options = len(rotate_options)

        boxes, new_w, new_h = self.get_boxes_and_new_size(box_size)
        for box in boxes:
            rotate = rotate_options[random.randint(0, n_options - 1)] if n_options > 1 else rotate_options[0]
            if rotate:
                region = self.image.crop(box)
                region = region.transpose(rotate)
                self.image.paste(region, box)
                log("Rotate box {}".format(box))

        self.image = self.image.crop((0, 0, new_w, new_h))

    def randomize_sections(self, box_size, ext):
        """
        Cuts the image into sections of side length box_size and randomly
        switches pairs of sections.

        box_size -- The length of each side of each box.
        ext -- The extension of the image
        """
        boxes, new_w, new_h = self.get_boxes_and_new_size(box_size)
        random.shuffle(boxes)

        pairs = []
        for i in range(0, len(boxes), 2):
            try: pairs.append((boxes[i], boxes[i + 1]))
            except IndexError: pass

        for pair in pairs:
            first_box, second_box = pair

            first_region_bytes = io.BytesIO()
            self.image.crop(first_box).save(first_region_bytes, format=ext)
            first_region = Image.open(first_region_bytes)

            second_region_bytes = io.BytesIO()
            self.image.crop(second_box).save(second_region_bytes, format=ext)
            second_region = Image.open(second_region_bytes)

            self.image.paste(first_region, second_box)
            self.image.paste(second_region, first_box)

            log("Switched boxes {}".format(pair))

        self.image = self.image.crop((0, 0, new_w, new_h))

    def get_boxes_and_new_size(self, box_size):
        """
        Returns the bounding boxes for as many sections of the image as possible
        using box_size as the length of each side of the box, along with the new
        height and width of the image.

        box_size -- The length of each side of each box.
        """
        w, h = self.image.size
        n_cols = w / box_size
        n_rows = h / box_size

        boxes = []
        if args.vertical:
            for i in range(n_cols):
                box = (i * box_size, 0, (i + 1) * box_size, h)
                boxes.append(box)

            return boxes, box_size * n_cols, h
        elif args.horizontal:
            for i in range(n_rows):
                box = (0, i * box_size, w, (i + 1) * box_size)
                boxes.append(box)
            return boxes, w, box_size * n_rows
        else:
            for i in range(n_rows):
                for j in range(n_cols):
                    box = (j * box_size, i * box_size,
                           (j + 1) * box_size, (i + 1) * box_size)
                    boxes.append(box)

            return boxes, box_size * n_cols, box_size * n_rows

    def save(self, save_path):
        """
        Saves the image

        save_path -- The file name for the image
        """
        self.image.save(save_path)

    def copy(self):
        """ Returns a copy of the image """
        return self.image.copy()

    def close(self):
        """ Close the image """
        self.image.close()

def log(message):
    """
    Simple logging method

    message -- The message to be logged
    """
    if DEBUG:
        print message

if __name__=='__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', type=str, help='Path to the image to\
        manipulate')
    parser.add_argument('-bs', '--box_size', default=2, type=int, help='The\
        size of the boxes the first frame will be split into')
    parser.add_argument('-i', '--iterations', default=None, type=int, help='The\
        number of times to run the manipulator, multiplying box_size by 2 for\
        each iteration')
    parser.add_argument('-v', '--vertical', action='store_true', help='Use flag\
        to use vertical strips instead of square boxes.')
    parser.add_argument('-ho', '--horizontal', action='store_true', help='Use\
        flag to use horizontal strips instead of square boxes.')
    parser.add_argument('-n', '--none', action='store_true', help='Use flag to\
        not rotate boxes.')
    parser.add_argument('-f', '--flip', action='store_true', help='Use flag to\
        flip each section instead of randomly rotating each section a multiple\
        of 90 degrees')
    parser.add_argument('-r', '--random', action='store_true', help='Use flag\
        to randomize position of boxes')
    parser.add_argument('--frames', action='store_true', help='Use flag to save\
        each frame along with the gif')
    parser.add_argument('--nogif', action='store_true', help='Use flag to not\
        create a gif with the resulting frames.')
    parser.add_argument('-o', '--output', default='', type=str, help="Path to\
        directory to save gif and/or frames in.")
    parser.add_argument('-d', '--debug', action='store_true', help='Use flag to\
        print debugging statements while the script runs')
    args = parser.parse_args()

    DEBUG = args.debug

    full_name, _ = os.path.splitext(args.image_path)
    base_name, ext = os.path.splitext(os.path.basename(args.image_path))
    if ext.lower() == '.jpg':
        copyfile(full_name + ext, full_name + '.jpeg')
        ext = '.jpeg'
    if os.path.exists(args.output):
        output = args.output
    else:
        output = os.path.dirname(full_name + ext) + '/'

    if args.flip:
        rotate_options = [Image.ROTATE_180]
    elif args.none or args.horizontal or args.vertical:
        rotate_options = [None]
    else:
        rotate_options =[None, Image.ROTATE_90, Image.ROTATE_180,
            Image.ROTATE_270]

    box_size = args.box_size
    box_sizes = []

    # Populate list of box_sizes
    iterations = args.iterations
    if iterations:
        for i in range(iterations):
            box_sizes.append(box_size)
            box_size *= 2
    else:
        image = Image.open(full_name + ext)
        size = image.size
        image.close()
        if args.vertical: min_size = size[0]
        elif args.horizontal: min_size = size[1]
        else: min_size = min(size)
        while box_size * 2 < min_size:
            box_sizes.append(box_size)
            box_size *= 2

    # Create frames
    frames = []
    for box_size in box_sizes:
        im = ImageManipulator(full_name + ext)
        im.rotate_sections(box_size, rotate_options)
        if args.random: im.randomize_sections(box_size, ext[1:])
        if args.frames or len(box_sizes) == 1:
            im.save('{}{}-{:03d}{}'.format(output, base_name, box_size, ext))
        frames.append(im.copy())
    frames.append(Image.open(full_name + ext))

    # Crop all frames to size of smallest frame
    min_w = min(map(lambda frame: frame.size[0], frames))
    min_h = min(map(lambda frame: frame.size[1], frames))
    frames = map(lambda frame: frame.crop((0, 0, min_w, min_h)), frames)

    # Loop the animation and save it
    middle_frames = frames[1:-1]
    middle_frames.reverse()
    if not args.nogif or len(box_sizes) == 1:
        images2gif.writeGif("{}{}{}.gif".format(output, base_name,
            "-random" if args.random else ""), frames + middle_frames)
