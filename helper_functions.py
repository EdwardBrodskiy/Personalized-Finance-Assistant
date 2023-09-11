import errno
import os
from collections import Counter
from itertools import chain


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


def get_hex(tk, color):
    rgb = tk.winfo_rgb(color)
    hex_color = "#{:02x}{:02x}{:02x}".format(rgb[0] // 256, rgb[1] // 256, rgb[2] // 256)
    return hex_color


def extract_tags(series):
    all_tags = list(chain.from_iterable(series))  # Flatten the list of tags
    tag_counts = Counter(all_tags)  # Count the frequency of each tag
    tag_counts_ordered = tag_counts.most_common()  # Order by popularity (most common first)
    only_tags = [tag for tag, _ in tag_counts_ordered]
    return only_tags


def ensure_dir_exists(path, is_file=False):
    dirpath = path
    if is_file:
        dirpath = os.path.dirname(path)
    if not os.path.exists(dirpath):
        try:
            os.makedirs(dirpath)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
