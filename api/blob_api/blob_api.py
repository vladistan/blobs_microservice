import hashlib
import os


def small():
    return 4


def sha1_of_file(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def prefix_from_sum(check_sum):
    return '/'.join((check_sum[0:2], check_sum[2:4]))


def make_store_dirs(store_prefix, file_dir):

    newdir = os.path.join(store_prefix, file_dir)

    if not os.path.exists(newdir):
           os.makedirs(newdir)
