import os, errno


def mkdir_p(path):
    """ 'mkdir -p' in Python """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def union_dicts(d1, d2):
    d = d1.copy()
    d.update(d2)
    return d
