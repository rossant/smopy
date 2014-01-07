Smopy
=====

Give a box in geographical coordinates (latitude/longitude), Smopy returns
an OpenStreetMap tile image at any zoom level!

```python
import smopy
map = smopy.Map((42., -1., 55., 3.), z=4)
map.show_ipython()
```
![Europe map](examples/europe.png)

[See the example notebook](http://nbviewer.ipython.org/github/rossant/smopy/blob/master/examples/example1.ipynb)

## Terms of use

This module fetches map images from [OpenStreetMap](http://www.openstreetmap.org/)'s servers. See the [usage policy](http://wiki.openstreetmap.org/wiki/Tile_usage_policy). In particular, **be careful not to retrieve large maps** as this can overload the servers.


