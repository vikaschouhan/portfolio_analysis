# Utility functions

from   PIL import Image
import glob
import os

def merge_images(file_list, out_file):
    im_size_list = []

    for f_this in file_list:
        im_size_list.append(Image.open(f_this).size)
    # endfor

    result_width  = max([x[0] for x in im_size_list])
    result_height = sum([x[1] for x in im_size_list])
    h_ptr_t = 0
    result  = Image.new('RGB', (result_width, result_height))

    # Iterate
    for f_this in file_list:
        im_this = Image.open(f_this)
        result.paste(im=im_this, box=(0, h_ptr_t))
        h_ptr_t = h_ptr_t + im_this.size[1]
    # endfor

    result.save(os.path.expanduser(out_file))
# enddef
