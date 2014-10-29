"""Smopy: OpenStreetMap image tiles in Python.

Give a box in geographical coordinates (latitude/longitude) and a zoom level,
Smopy returns an OpenStreetMap tile image!

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import math
from six import BytesIO
from six.moves.urllib.request import urlopen

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display_png


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
__version__ = '0.0.3'
TILE_SIZE = 256
MAXTILES = 20


# -----------------------------------------------------------------------------
# OSM functions
# -----------------------------------------------------------------------------
def get_url(x, y, z):
    """Return the URL to the image tile (x, y) at zoom z."""
    return "http://tile.openstreetmap.org/{z}/{x}/{y}.png".format(z=z, x=x, y=y)

def fetch_tile(x, y, z):
    """Fetch tile (x, y) at zoom level z from OpenStreetMap's servers.

    Return a PIL image.

    """
    url = get_url(x,y,z)
    png = BytesIO(urlopen(url).read())
    img = Image.open(png)
    img.load()
    return img

def fetch_map(box, z):
    """Fetch OSM tiles composing a box at a given zoom level, and
    return the assembled PIL image."""
    x0, y0, x1, y1 = box
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    x0 = max(0, x0)
    x1 = min(2**z-1, x1)
    y0 = max(0, y0)
    y1 = min(2**z-1, y1)
    sx, sy = x1 - x0 + 1, y1 - y0 + 1
    if sx+sy >= MAXTILES:
        raise Exception(("You are requesting a very large map, beware of "
                 "OpenStreetMap tile usage policy "
                 "(http://wiki.openstreetmap.org/wiki/Tile_usage_policy)."))
    img = Image.new('RGB', (sx*TILE_SIZE, sy*TILE_SIZE))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            px, py = TILE_SIZE * (x - x0), TILE_SIZE * (y - y0)
            img.paste(fetch_tile(x, y, z), (px, py))
    return img


# -----------------------------------------------------------------------------
# Utility imaging functions
# -----------------------------------------------------------------------------
def image_to_png(img):
    """Convert a PIL image to a PNG binary string."""
    exp = BytesIO()
    img.save(exp, format='png')
    exp.seek(0)
    s = exp.read()
    exp.close()
    return s

def image_to_numpy(img):
    """Convert a PIL image to a NumPy array."""
    return np.array(img)


# -----------------------------------------------------------------------------
# Functions related to coordinates
# -----------------------------------------------------------------------------
def deg2num(lat_deg, lon_deg, zoom, do_round=True):
    """Convert from latitude and longitude to tile numbers.

    If do_round is True, return integers. Otherwise, return floating point
    values.

    Source: http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python

    """
    lat_rad = np.radians(lat_deg)
    n = 2.0 ** zoom
    if do_round:
        f = np.floor
    else:
        f = lambda x: x
    xtile = f((lon_deg + 180.0) / 360.0 * n)
    ytile = f((1.0 - np.log(np.tan(lat_rad) + (1 / np.cos(lat_rad))) / np.pi) / 2.0 * n)
    if do_round:
        if isinstance(xtile, np.ndarray):
            xtile = xtile.astype(np.int32)
        else:
            xtile = int(xtile)
        if isinstance(ytile, np.ndarray):
            ytile = ytile.astype(np.int32)
        else:
            ytile = int(ytile)
    return (xtile, ytile)

def get_tile_box(box_latlon, z):
    """Convert a box in geographical coordinates to a box in
    tile coordinates (integers), at a given zoom level.

    box_latlon is lat0, lon0, lat1, lon1.

    """
    lat0, lon0, lat1, lon1 = box_latlon
    x0, y0 = deg2num(lat0, lon0, z)
    x1, y1 = deg2num(lat1, lon1, z)
    return (x0, y0, x1, y1)

def get_tile_coords(lat, lon, z):
    """Convert geographical coordinates to tile coordinates (integers),
    at a given zoom level."""
    return deg2num(lat, lon, z, do_round=False)

def _box(*args):
    """Return a tuple (lat0, lon0, lat1, lon1) from a coordinate box that
    can be specified in multiple ways:

    A. box((lat0, lon0))  # nargs = 1
    B. box((lat0, lon0, lat1, lon1))  # nargs = 1
    C. box(lat0, lon0)  # nargs = 2
    D. box((lat0, lon0), (lat1, lon1))  # nargs = 2
    E. box(lat0, lon0, lat1, lon1)  # nargs = 4

    """
    nargs = len(args)
    assert nargs in (1, 2, 4)
    pos1 = None

    # Case A.
    if nargs == 1:
        assert hasattr(args[0], '__len__')
        pos = args[0]
        assert len(pos) in (2, 4)
        if len(pos) == 2:
            pos0 = pos
        elif len(pos) == 4:
            pos0 = pos[:2]
            pos1 = pos[2:]

    elif nargs == 2:
        # Case C.
        if not hasattr(args[0], '__len__'):
            pos0 = args[0], args[1]
        # Case D.
        else:
            pos0, pos1 = args[0], args[1]

    # Case E.
    elif nargs == 4:
        pos0 = args[0], args[1]
        pos1 = args[2], args[3]

    if pos1 is None:
        pos1 = pos0

    return (pos0[0], pos0[1], pos1[0], pos1[1])

def extend_box(box_latlon, margin=.1):
    """Extend a box in geographical coordinates with a relative margin."""
    (lat0, lon0, lat1, lon1) = box_latlon
    lat0, lat1 = min(lat0, lat1), max(lat0, lat1)
    lon0, lon1 = min(lon0, lon1), max(lon0, lon1)
    dlat = (lat1 - lat0)
    dlon = (lon1 - lon0)
    return (lat0 - dlat * margin, lon0 - dlon * margin,
            lat1 + dlat * margin, lon1 + dlon * margin)


# -----------------------------------------------------------------------------
# Main Map class
# -----------------------------------------------------------------------------
class Map(object):
    """Represent an OpenStreetMap image.

    Initialized as:

        map = Map((lat_min, lon_min, lat_max, lon_max), z=z)

    where the first argument is a box in geographical coordinates, and z
    is the zoom level (from minimum zoom 1 to maximum zoom 19).

    Methods:

    * To display in the IPython notebook: `map.show_ipython()`.

    * To create a matplotlib plot: `ax = map.show_mpl()`.

    * To save a PNG: `map.save_png(filename)`.

    """
    def __init__(self, *args, **kwargs):
        """Create and fetch the map with a given box in geographical
        coordinates.

        Can be called with `Map(box, z=z)` or `Map(lat, lon, z=z)`.

        """
        z = kwargs.get('z', 3)
        margin = kwargs.get('margin', None)
        box = _box(*args)
        if margin is not None:
            box = extend_box(box, margin)
        self.box = box
        self.z = z
        self.box_tile = get_tile_box(self.box, self.z)
        self.xmin = min(self.box_tile[0], self.box_tile[2])
        self.ymin = min(self.box_tile[1], self.box_tile[3])
        self.img = None
        self.fetch()

    def to_pixels(self, lat, lon=None):
        """Convert from geographical coordinates to pixels in the image."""
        return_2D = False
        if lon is None:
            if isinstance(lat, np.ndarray):
                assert lat.ndim == 2
                assert lat.shape[1] == 2
                lat, lon = lat.T
                return_2D = True
            else:
                lat, lon = lat
        x, y = get_tile_coords(lat, lon, self.z)
        px = (x - self.xmin) * TILE_SIZE
        py = (y - self.ymin) * TILE_SIZE
        if return_2D:
            return np.c_[px, py]
        else:
            return px, py

    def fetch(self):
        """Fetch the image from OSM's servers."""
        if self.img is None:
            self.img = fetch_map(self.box_tile, self.z)
        self.w, self.h = self.img.size
        return self.img

    def show_mpl(self, ax=None, figsize=None, dpi=None):
        """Show the image in matplotlib."""
        if not ax:
            plt.figure(figsize=figsize, dpi=dpi)
            ax = plt.subplot(111)
            plt.xticks([]);
            plt.yticks([]);
            plt.grid(False)
            plt.xlim(0, self.w);
            plt.ylim(self.h, 0)
            plt.axis('off');
            plt.tight_layout();
        ax.imshow(self.img);
        return ax

    def show_ipython(self):
        """Show the image in IPython as a PNG image."""
        png = image_to_png(self.img)
        display_png(png, raw=True)

    def to_pil(self):
        """Return the PIL image."""
        return self.img

    def to_numpy(self):
        """Return the image as a NumPy array."""
        return image_to_numpy(self.img)

    def save_png(self, filename):
        """Save the image to a PNG file."""
        png = image_to_png(self.img)
        with open(filename, 'wb') as f:
            f.write(png)

