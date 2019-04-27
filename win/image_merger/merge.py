import sys
import os
import glob
import argparse
from PIL import Image

def_name = 'merged.png'
def_outpath = f'.{os.sep}{def_name}'
parser = argparse.ArgumentParser(
    description='Image merger for animation sprites',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i', '--input',
    dest='input',
    help='input glob with wildcards',
    default='./*.png')
parser.add_argument('-o', '--output',
    dest='output',
    help='path of the output file with name',
    default=def_outpath)
parser.add_argument('-v', '--verbose',
    action='store_true')
args = parser.parse_args()

args.input = args.input.replace('\\', os.sep).replace('/', os.sep)
inputpath_base = os.path.abspath(args.input.rsplit(os.sep)[0])
if args.output == def_outpath:
    args.output = inputpath_base + os.sep + def_name
args.output = os.path.abspath(args.output)

files = list(map(lambda f: os.path.abspath(f), glob.glob(args.input)))
files = [f for f in files if f != args.output]

if args.verbose:
    print(f'output:\n  {args.output}')
    print('intput:')
    for f in files: print(f'  {f}')

if len(files) < 2:
    print(f'[ERROR] Not enouh image in {inputpath_base}')
    sys.exit()

images = list(map(Image.open, files))

widths, heights = zip(*(i.size for i in images))
total_width = sum(widths)
max_height = max(heights)

new_im = Image.new('RGBA', (total_width, max_height))

x_offset = 0
for im in images:
    new_im.paste(im, (x_offset,0))
    x_offset += im.size[0]

new_im.save(args.output, 'png')
