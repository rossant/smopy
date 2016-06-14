Smopy
=====

**New: you may be interested in [Folium](https://github.com/wrobstory/folium) for interactive maps with Leaflet.js**

Give a box in geographical coordinates (latitude/longitude) and a zoom level, Smopy returns an OpenStreetMap tile image!

```python
import smopy
map = smopy.Map((42., -1., 55., 3.), z=4)
map.show_ipython()
```
![Europe map](examples/europe.png)

You can also import the map in matplotlib and convert from geographical coordinates to pixels easily.

```python
x, y = map.to_pixels(48.86151, 2.33474)
ax = map.show_mpl(figsize=(8, 6))
ax.plot(x, y, 'or', ms=10, mew=2);
```
![Europe map](examples/europe2.png)

Alternative OSM tile servers can be used as well. An example is in the example notebook.

[See the example notebook](http://nbviewer.ipython.org/github/rossant/smopy/blob/master/examples/example1.ipynb)

## Installation

Smopy currently requires:

* Pillow
* NumPy
* matplotlib
* IPython

To install, `pip install smopy` or:

```python
git clone git@github.com:rossant/smopy.git
cd smopy
python setup.py develop
```


## Terms of use

This module fetches image maps from [OpenStreetMap](http://www.openstreetmap.org/)'s servers. See the [usage policy](http://wiki.openstreetmap.org/wiki/Tile_usage_policy). In particular, **be careful not to retrieve large maps** as this can overload the servers.


