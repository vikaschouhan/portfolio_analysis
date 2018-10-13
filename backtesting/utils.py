import os
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt
import PIL.Image
import pdf2image.pdf2image
import numpy as np

def rp(path):
    return os.path.expanduser(path)
# enddef

def cdir(d_path):
    d_path = rp(d_path)
    if not os.path.isdir(d_path):
        os.mkdir(d_path)
    # endif
    return d_path
# enddef

def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    # endif
# enddef

def to_precision(x, precision=2):
    return int(x * 10**precision)/(10**precision * 1.0)
# enddef

def save_figs_to_pdf(pdf_file, figs, width=48, height=9, close_figs=True):
    if isinstance(figs, dict):
        figs = list(figs.values())
    elif isinstance(figs, list):
        pass
    else:
        figs = [figs]
    # endif
    # Pdf plot
    pdf = matplotlib.backends.backend_pdf.PdfPages(rp(pdf_file))
    for fig in figs:
        fig.set_size_inches(width, height)
        pdf.savefig(fig)
    # endfor
    pdf.close()
    if close_figs:
        for fig in figs:
            plt.close(fig)
        # endfor
    # endif
# enddef

# stitch source and target together
def join_images_vertical(image_list, file_name=None):
    assert isinstance(image_list, list), 'image_list is not list.'

    im0_shape = image_list[0].shape
    # Check shape
    for img_t in image_list[1:]:
        assert im0_shape == img_t.shape, "Shapes of images do not match."
    # endfor

    n_images       = len(image_list)
    img_width      = image_list[0].shape[1]
    img_height     = image_list[0].shape[0]
    new_img_width  = img_width
    new_img_height = img_height * n_images

    new_im = PIL.Image.new('RGB', (new_img_width, new_img_height)) #creates a new empty image, RGB mode, and size 444 by 95

    for index_t in range(len(image_list)):
        new_im.paste(PIL.Image.fromarray(image_list[index_t]), (0, img_height * index_t))
    # endfor

    if file_name:
        new_im.save(file_name)
    # endif
    return np.asarray(new_im)
# endif

def save_multiple_figs_to_image_file(fig_list, out_image, width=16, height=9, close_figs=True):
    tmp_pdf = '/tmp/______tmp_pdf'
    save_figs_to_pdf(tmp_pdf, fig_list, width=width, height=height, close_figs=True)
    # Convert pdf to images
    image_list = [np.asarray(x) for x in pdf2image.convert_from_path(tmp_pdf)]
    # Join images & save file
    join_images_vertical(image_list, out_image)
# enddef
