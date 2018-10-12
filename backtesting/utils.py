import os
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt

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
