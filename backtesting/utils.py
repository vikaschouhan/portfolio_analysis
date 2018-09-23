import os

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

def to_precision(x, precision=2):
    return int(x * 10**precision)/(10**precision * 1.0)
# enddef
