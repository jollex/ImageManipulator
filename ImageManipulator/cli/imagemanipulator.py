#!/usr/bin/env python

import argparse, sys, os, random, io, json
from shutil import copyfile
from PIL import Image
import images2gif

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']

class ImageManipulator(object):
    """
    Class for manipulating an Image. It is created using the path to an image
    file, a box_size, and an arguments object containging configuration
    information that is used to interpret the box size. For example, if the
    horizontal or vertical options are selected, then the boxes are done as
    slices across the image, instead of square boxes.
     """
    def __init__(self, image_path, box_size, args):
        """
        :param image_path: The path to the image file.
        :param box_size: The size of a box. This is used to split the image into
        boxes and manipulate them.
        :param args: The args object containing configuration values.
        """
        self.image = Image.open(image_path)
        self.args = args
        if args.resize:
            self.resize()
        self.box_size = box_size
        self.boxes, self.new_w, self.new_h = self.get_boxes_and_size(box_size)
        self.ext = os.path.splitext(image_path)[1][1:]

    def resize(self):
        """
        Resizes the image according to the arguments provided. If either the
        width or height provided is zero, the other dimension is caluclated
        from the dimension provided.
        """
        cur_width, cur_height = self.image.size
        width, height = args.resize

        if width == 0 and height != 0:
            width = int((float(cur_width) / float(cur_height)) * height)
        elif width != 0 and height == 0:
            height = int((float(cur_height) / float(cur_width)) * width)

        self.image = self.image.resize((width, height))
        self.log('Resized image to ({}, {})'.format(width, height))

    def get_boxes_and_size(self, box_size):
        """
        Returns the bounding boxes for as many sections of the image as possible
        using box_size as the length of each side of the box, along with the new
        height and width of the image.

        :param box_size: The length of each side of each box
        :return: A tuple (boxes, new_w, new_h); where boxes is a list of tuples
        (left, up, right, down) where each direction is the position of that
        side of the box, and new_w and new_h are the new dimensions of the
        image.
        """
        if box_size == 0:
            w, h = self.image.size
            return [(0, 0, w, h)], w, h
        if args.vertical:
            return self.get_vertical_boxes_and_size(box_size)
        elif args.horizontal:
            return self.get_horizontal_boxes_and_size(box_size)
        else:
            return self.get_square_boxes_and_size(box_size)

    def get_vertical_boxes_and_size(self, box_size):
        """
        Returns vertical slices of width box_size, along with the new
        dimensions of the image.

        :param box_size: The width of one vertical slice.
        :return: A tuple (boxes, new_w, new_h); where boxes is a list of tuples
        (left, up, right, down) where each direction is the position of that
        side of the box, and new_w and new_h are the new dimensions of the
        image.
        """
        w, h = self.image.size
        n_cols = w / box_size
        boxes = []
        for i in range(n_cols):
            box = (i * box_size, 0, (i + 1) * box_size, h)
            boxes.append(box)
        return boxes, box_size * n_cols, h

    def get_horizontal_boxes_and_size(self, box_size):
        """
        Returns horizontal slices of height box_size, along with the new
        dimensions of the image.

        :param box_size: The height of one horizontal slice.
        :return: A tuple (boxes, new_w, new_h); where boxes is a list of tuples
        (left, up, right, down) where each direction is the position of that
        side of the box, and new_w and new_h are the new dimensions of the
        image.
        """
        w, h = self.image.size
        n_rows = h / box_size
        boxes = []
        for i in range(n_rows):
            box = (0, i * box_size, w, (i + 1) * box_size)
            boxes.append(box)
        return boxes, w, box_size * n_rows

    def get_square_boxes_and_size(self, box_size):
        """
        Returns square boxes of side length box_size, along with the new
        dimensions of the image.

        :param box_size: The side length of a box
        :return: A tuple (boxes, new_w, new_h); where boxes is a list of tuples
        (left, up, right, down) where each direction is the position of that
        side of the box, and new_w and new_h are the new dimensions of the
        image.
        """
        w, h = self.image.size
        n_rows = h / box_size
        n_cols = w / box_size
        boxes = []
        for i in range(n_rows):
            for j in range(n_cols):
                box = (j * box_size, i * box_size, (j + 1) * box_size,
                       (i + 1) * box_size)
                boxes.append(box)

        return boxes, box_size * n_cols, box_size * n_rows

    def rotate_sections(self, rotate_options):
        """
        Cuts the image into sections of side length box_size and rotates each
        one using a randomly selected rotation from rotate_options.

        :param rotate_options: A non-empty list of RotateOptions. A RotateOption
        is one of None, Image.ROTATE_90, Image.ROTATE_180, or Image.ROTATE_270.
        """
        if (self.box_size == 1
            and not (self.args.vertical or self.args.horizontal)):
            return

        n_options = len(rotate_options)

        if n_options == 1:
            for box in self.boxes:
                self.rotate_box(box, rotate_options[0])
        else:
            for box in self.boxes:
                rotate_option = rotate_options[random.randint(0, n_options - 1)]
                self.rotate_box(box, rotate_option)

    def rotate_box(self, box, rotate_option):
        """
        Rotates the given box using the given RotateOption.

        :param box: The box to be rotate.
        :param rotate_option: The RotateOption
        """
        if rotate_option is not None:
            region = self.image.crop(box)
            region = region.transpose(rotate_option)
            self.image.paste(region, box)
            self.log("Rotated box {}".format(box))

    def randomize_sections(self):
        """
        Cuts the image into sections of side length box_size and randomly
        switches pairs of sections.
        """
        boxes = list(self.boxes)
        random.shuffle(boxes)

        pairs = []
        for i in range(0, len(boxes), 2):
            try: pairs.append((boxes[i], boxes[i + 1]))
            except IndexError: pass

        for first_box, second_box in pairs:
            self.swap_boxes(first_box, second_box, self.ext)

    def swap_boxes(self, first_box, second_box, ext):
        """
        Swaps the two boxes on the image.

        :param first_box: The first box to swap.
        :param second_box: The other box to swap with the first.
        :param ext: The extension of the image file, needed to save the images
        bytes.
        """
        first_region_bytes = io.BytesIO()
        self.image.crop(first_box).save(first_region_bytes, format=ext)
        first_region = Image.open(first_region_bytes)

        second_region_bytes = io.BytesIO()
        self.image.crop(second_box).save(second_region_bytes, format=ext)
        second_region = Image.open(second_region_bytes)

        self.image.paste(first_region, second_box)
        self.image.paste(second_region, first_box)

        self.log("Swapped boxes {}".format((first_box, second_box)))

    def average_sections(self):
        """
        Turns each box into an average of all the pixels in the box.
        """
        if (self.box_size == 1
            and not (self.args.vertical or self.args.horizontal)):
            return

        for box in self.boxes:
            self.average_box(box)
            self.log("Averaged box {}".format(box))

    def average_box(self, box):
        """
        Averages one box.

        :param box: The box to average.
        """
        region = self.image.crop(box)
        w, h = region.size
        pixels = region.load()

        rs, gs, bs = [], [], []
        for x in range(w):
            for y in range(h):
                pixel = pixels[x, y]
                rs.append(pixel[0])
                gs.append(pixel[1])
                bs.append(pixel[2])

        r = sum(rs) / len(rs)
        g = sum(gs) / len(gs)
        b = sum(bs) / len(bs)

        self.image.paste(Image.new('RGB', (w, h), (r, g, b)), box)

    def crop_image(self):
        """
        Effect: crops the image to the new dimenstions returned when calculating
        the boxes.
        """
        self.image = self.image.crop((0, 0, self.new_w, self.new_h))

    def copy(self):
        """ :return: A copy of the current Image. """
        return self.image.copy()

    def save(self, save_path):
        """
        Saves the current image.

        :param save_path: The file path to save the image to.
        """
        self.image.save(save_path)

    def close(self):
        """ Effect: closes the Image. """
        self.image.close()

    def log(self, message):
        """
        Simply prints message to STDOUT if debugging is enabled.

        :param message: The message to be logged.
        """
        if self.args.debug:
            print message

def manipulate_image(image_path, args):
    """
    Performs all image operations on the given image file

    :param image_path: path to the image file to edit
    """
    full_name, _ = os.path.splitext(image_path)
    base_name, ext = os.path.splitext(os.path.basename(image_path))
    if ext.lower() == '.jpg':
        os.rename(full_name + ext, full_name + '.jpeg')
        ext = '.jpeg'

    if args.output and os.path.exists(args.output):
        output = os.path.abspath(args.output)
    else:
        output = os.path.dirname(full_name + ext)

    box_sizes = get_box_sizes(args.box_size, args.iterations, full_name + ext, args)
    frames, frame_paths = [], []
    for box_size in box_sizes:
        im = ImageManipulator(full_name + ext, box_size, args)
        rotate_options = get_rotate_options(args)
        if len(rotate_options) != 0:
            im.rotate_sections(rotate_options)
        if args.average:
            im.average_sections()
        if args.random:
            im.randomize_sections()
        im.crop_image()
        if args.frames or len(box_sizes) == 1:
            filename = '{}-{:04d}{}'.format(base_name, box_size, ext)
            im.save(os.path.join(output, filename))
            frame_paths.append(filename)
        frames.append(im.copy())

    # Crop all frames to size of smallest frame
    min_w = min(map(lambda frame: frame.size[0], frames))
    min_h = min(map(lambda frame: frame.size[1], frames))
    frames = map(lambda frame: frame.crop((0, 0, min_w, min_h)), frames)

    # Loop the animation and save it
    middle_frames = frames[1:-1]
    middle_frames.reverse()
    if not (args.nogif or len(box_sizes) == 1):
        gif_path = base_name + ".gif"
        images2gif.writeGif(os.path.join(output, gif_path),
            frames + middle_frames)
    else:
        gif_path =  ''

    image_paths = {'gif': gif_path, 'frames': frame_paths}
    print json.dumps(image_paths)

def get_box_sizes(initial_box_size, iterations, image_path, args):
    """
    Creates a list of integers, where each integer is the box size for the
    manipulations of the image for that frame. This is done by taking a starting
    box size and multiplying it by two every iteration. If the auto flag is
    given the iterations will continue until they are at half the size of one
    of the sides of the image.

    :param initial_box_size: The beginning box_size.
    :param iterations: The number of iterations.
    :param image_path: The path to the image.
    :param args: The args object used for configuration.

    :return: A list of integers.
    """
    box_sizes = []
    box_size = 1 if args.auto else initial_box_size
    if args.auto:
        image = Image.open(image_path)
        size = image.size
        image.close()

        if args.vertical: max_size = size[0]
        elif args.horizontal: max_size = size[1]
        else: max_size = min(size)

        while box_size * 2 <= max_size:
            box_sizes.append(box_size)
            box_size *= 2 # also the most important line
    else:
        for i in range(iterations):
            box_sizes.append(box_size)
            box_size *= 2 # the most important line
    return box_sizes

def get_rotate_options(args):
    """
    Gets the rotate options for the Image depending on the arguments.
    :param args: The args object used for configuration.
    :return: A list of RotateOptions. A RotateOption is one of None,
    Image.ROTATE_90, Image.ROTATE_180, or Image.ROTATE_270.
    """
    if args.flip:
        return [Image.ROTATE_180]
    elif args.ninety:
        return [None, Image.ROTATE_90, Image.ROTATE_180, Image.ROTATE_270]
    else:
        return []

if __name__=='__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', nargs='?', default='', type=str,
        help='Path to the image to manipulate')
    parser.add_argument('-rs', '--resize', nargs=2, metavar=('X', 'Y'),
        default=False, type=int, help='The dimensions to resize the image to\
        before manipulating it. Powers of two are recommended. Set either x\
        or y to 0 to dynamically determine it from the other dimension')
    parser.add_argument('-bs', '--box_size', default=0, type=int, help='The\
        size of the boxes the first frame will be split into')
    parser.add_argument('-i', '--iterations', default=1, type=int, help='The\
        number of times to run the manipulator, multiplying box_size by 2 for\
        each iteration')
    parser.add_argument('--auto', action='store_true', help='Automatically\
        create a GIF going from box size 1 to min(width, height) / 2')
    parser.add_argument('-v', '--vertical', action='store_true', help='Use\
        vertical strips instead of square boxes')
    parser.add_argument('-ho', '--horizontal', action='store_true', help='Use\
        horizontal strips instead of square boxes.')
    parser.add_argument('-f', '--flip', action='store_true', help='Flip each\
        box')
    parser.add_argument('-n', '--ninety', action='store_true', help='Rotate\
        each box a random multiple of ninety degrees')
    parser.add_argument('-r', '--random', action='store_true', help='Randomize\
        position of boxes')
    parser.add_argument('-a', '--average', action='store_true', help='Color\
        each box the average color of its pixels')
    parser.add_argument('--frames', action='store_true', help='Save each frame\
        along with the gif')
    parser.add_argument('--nogif', action='store_true', help='Do not create a\
        gif with the resulting frames')
    parser.add_argument('-o', '--output', default='', type=str, help='Path to\
        directory to save gif and/or frames in')
    parser.add_argument('-dir', '--directory', default='', type=str,
        help='Directory containing image files to do operations on, recursive.')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    if args.directory:
        for dirpath, dirnames, filenames in os.walk(args.directory):
            for name in filenames:
                _, ext = os.path.splitext(name)
                if ext in IMAGE_EXTENSIONS:
                    manipulate_image(os.path.join(dirpath, name), args)
    elif args.image_path != '':
        manipulate_image(args.image_path, args)
    else:
        parser.print_help()
