"""
main module of project
"""

import pandas as pd
import folium


map = folium.Map()
map = folium.Map(tiles="Stamen Terrain")
map.save('Map_1.html')


if __name__ == '__main__':
    pass
