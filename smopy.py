import math
import urllib2
import cStringIO

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display_png

__version__ = '0.0.1'
TILE_SIZE = 256
MAXTILES = 20

def deg2num(lat_deg, lon_deg, zoom, do_round=True):
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

def get_url(x, y, z):
    # x = np.clip(x, 0, 2 ** z - 1)
    # y = np.clip(y, 0, 2 ** z - 1)
    return "http://tile.openstreetmap.org/{z}/{x}/{y}.png".format(z=z, x=x, y=y)

def get_tile(x, y, z):
    url = get_url(x,y,z)
    png = cStringIO.StringIO(urllib2.urlopen(url).read())
    img = Image.open(png)
    img.load()
    return img

def image_to_png(img):
    exp = cStringIO.StringIO()
    img.save(exp, format='png')
    exp.reset()
    s = exp.read()
    exp.close()
    return s

def image_to_numpy(img):
    return np.array(img)
    
def fetch_map(box, z):
    x0, y0, x1, y1 = box
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    x0 = max(0, x0)
    x1 = min(2**z-1, x1)
    y0 = max(0, y0)
    y1 = min(2**z-1, y1)
    sx, sy = x1 - x0 + 1, y1 - y0 + 1
    if sx+sy >= MAXTILES:
        raise ArgumentError(("You are requesting a very large map, beware of "
                 "OpenStreetMap tile usage policy "
                 "(http://wiki.openstreetmap.org/wiki/Tile_usage_policy)."))
    img = Image.new('RGB', (sx*TILE_SIZE, sy*TILE_SIZE))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            px, py = TILE_SIZE * (x - x0), TILE_SIZE * (y - y0)
            img.paste(get_tile(x, y, z), (px, py))
    return img

def get_tile_box(box_latlon, z):
    lat0, lon0, lat1, lon1 = box_latlon
    x0, y0 = deg2num(lat0, lon0, z)
    x1, y1 = deg2num(lat1, lon1, z)
    return (x0, y0, x1, y1)

def get_tile_coords(lat, lon, z):
    return deg2num(lat, lon, z, do_round=False)

def extend_box(box, margin=.1):
    (lat0, lon0, lat1, lon1) = box
    lat0, lat1 = min(lat0, lat1), max(lat0, lat1)
    lon0, lon1 = min(lon0, lon1), max(lon0, lon1)
    dlat = (lat1 - lat0)
    dlon = (lon1 - lon0)
    return (lat0 - dlat * margin, lon0 - dlon * margin, 
            lat1 + dlat * margin, lon1 + dlon * margin)

class Map(object):
    def __init__(self, box, lon=None, z=3):
        if not hasattr(box, '__len__'):
            assert lon is not None
            box = (box, lon)
        if len(box) == 2:
            box = (box[0], box[1], box[0], box[1])
        self.box = box
        self.z = z
        self.box_tile = get_tile_box(self.box, self.z)
        self.xmin = min(self.box_tile[0], self.box_tile[2])
        self.ymin = min(self.box_tile[1], self.box_tile[3])
        self.img = None
        self.fetch()
    
    def to_pixels(self, lat, lon=None):
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
        if self.img is None:
            self.img = fetch_map(self.box_tile, self.z)
        self.w, self.h = self.img.size
        return self.img
    
    def show_mpl(self, ax=None, figsize=None, dpi=None):
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
        png = image_to_png(self.img)
        display_png(png, raw=True)

    def to_pil(self):
        return self.img
        
    def to_numpy(self):
        return image_to_numpy(self.img)
        
    def save_png(self, filename):
        png = image_to_png(self.img)
        with open(filename, 'wb') as f:
            f.write(png)
        