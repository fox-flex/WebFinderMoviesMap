"""
main module of project
"""

from random import uniform
import warnings
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from haversine import haversine

warnings.filterwarnings('ignore')
geolocator = Nominatim(user_agent="super_puper_extra_important_request")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)


def place_coordinates(name: str) -> dict:
    """
    function return dict of coordinates of place.
    exact coordinates and range where can be that place.
    >>> place_coordinates('Ukraine')
    {'coordinates': ('49.4871968', '31.2718321'), \
'coordinates_range': ['44.184598', '52.3797464', '22.137059', '40.2275801']}
    """
    try:
        info = geolocator.geocode(name).raw
        return {'coordinates':(info['lat'], info['lon']),
                'coordinates_range':info['boundingbox']}
    except AttributeError:
        pass


def read_info(coordinates: tuple, year: int,
              path='./database/locations.list',
              path_cont='./database/Countries-Continents.csv') -> pd.DataFrame:
    """
    function read data from the database and return dataset whit info
    about films
    """
    pos = str(coordinates[0]) + ', ' + str(coordinates[1])
    country = geolocator.reverse(pos, timeout=10, exactly_one=True,
                                 language='en').raw['address']['country']
    if country == 'United States':
        country = 'USA'
    if country == 'United Kingdom':
        country = 'UK'

    continent = None
    continents = {}
    with open(path_cont, 'r', encoding='latin-1') as file:
        file.readline()
        for cont0, countr0 in map(lambda x: x.strip().split(','),
                                  file.readlines()):
            try:
                continents[cont0].add(countr0)
            except KeyError:
                continents[cont0] = {countr0}
            if countr0 == country:
                continent = cont0
    if continent:
        countries = continents[continent]
    else:
        countries = set()
        for some_countries in continents.items():
            countries |= some_countries

    names = set()
    with open(path, 'r', encoding='latin-1') as file:
        for _ in range(14):
            file.readline()
        info = pd.DataFrame(columns=['place', 'films', 'coordinates',
                                     'range', 'distance'])
        for line in file.readlines()[:-1]:
            line = list(map(lambda x: x.strip(), line.split('\t')))
            line = list(filter(None, line))
            name_line, place = line[:2]
            try:
                ind = name_line.index('"', 2)
                name = name_line[1:ind]
                year0 = name_line[ind + 3:ind + 7]
            except ValueError:
                ind = name_line.index('(') - 1
                name = name_line[0:ind]
                year0 = name_line[ind + 2:ind + 6]
            names.add(name)
            bul = False
            if year0 == str(year):
                for cntr in countries:
                    if cntr in place:
                        bul = True
                        break
            if not bul:
                continue
            try:
                index = info.index[info['place'] == place][0]
                info['films'][index].add(name)
            except IndexError:
                try:
                    pos = place_coordinates(line[-1])
                    coord = tuple(map(float, pos['coordinates']))
                    distance = -1 * haversine(coordinates, coord)
                    info = info.append({'place': place,
                                        'films': {name},
                                        'coordinates': pos['coordinates'],
                                        'range': pos['coordinates_range'],
                                        'distance': distance},
                                       ignore_index=True)
                except AttributeError:
                    continue
                except TypeError:
                    continue
                except GeocoderUnavailable:
                    break
    for i in info.index:
        info['films'][i] = frozenset(info['films'][i])
        info['range'][i] = tuple(info['range'][i])
    return info


def create_points(data_base: pd.DataFrame, num_of_points=10) -> dict:
    """
    function return 10 most nearby places where was maiden movies
    """
    data_base = data_base.nlargest(num_of_points, 'distance')
    data_base.reset_index(drop=True, inplace=True)
    points = {}
    i = 0
    num_points = 0
    while num_points < num_of_points:
        try:
            data_base['films'][i]
        except KeyError:
            break
        if len(data_base['films'][i]) == 1:
            coord = tuple(map(float, data_base['coordinates'][i]))
            try:
                _ = points[coord]
                coord1 = uniform(coord[0] - 0.025, coord[0] + 0.025)
                coord2 = uniform(coord[1] - 0.025, coord[1] + 0.025)
                coord = (coord1, coord2)
            except KeyError:
                pass
            points[coord], *_ = data_base['films'][i]
            num_points += 1
        else:
            for name in data_base['films'][i]:
                coord = list(map(float, data_base['range'][i]))
                coord11 = coord[0]
                coord12 = coord[1]
                if coord12 - coord11 < 0.05:
                    coord11 = (coord11 + coord12) / 2 - 0.025
                    coord12 = (coord11 + coord12) / 2 + 0.025
                coord1 = uniform(coord11, coord12)
                coord21 = coord[2]
                coord22 = coord[3]
                if coord22 - coord21 < 0.05:
                    coord21 = (coord21 + coord22) / 2 - 0.025
                    coord22 = (coord21 + coord22) / 2 + 0.025
                coord2 = uniform(coord21, coord22)

                points[(coord1, coord2)] = name
                num_points += 1
                if num_points == num_of_points:
                    break
        i += 1
    return points


def create_map(coordinates: tuple, year: int):
    """
    function create web map in html format in which are marked points
    """
    points = create_points(read_info(coordinates, year))

    map0 = folium.Map(location=coordinates, zoom_start=5)

    tooltip = "Hype!"

    map0.add_child(folium.Marker(location=coordinates,
                                popup="You are here!",
                                icon=folium.Icon(color='red', icon='adjust')))

    point_layer = folium.FeatureGroup(name="Films Search")

    for pos in points:
        point_layer.add_child(folium.Marker(location=pos,
                                            popup=points[pos],
                                            icon=folium.Icon(icon='cloud'),
                                            tooltip=tooltip))

    map0.add_child(point_layer)

    # add one more layer

    fg_pp = folium.FeatureGroup(name="The furthest film")
    fg_pp.add_child(folium.GeoJson(data=open('./database/world.json', 'r',
        encoding='utf-8-sig').read(),
        style_function=lambda x:{'fillColor': 'green'
        if x['properties']['POP2005'] < 10000000 else 'orange'
        if 10000000 <= x['properties']['POP2005'] < 20000000 else 'red'}))
    # map0.add_child(fg_hc)
    map0.add_child(fg_pp)
    map0.add_child(folium.LayerControl())

    map0.save('map.html')


def main():
    """
    main function of crating map
    """
    # year = '2020'
    # position = '49.842957, 24.031111'  # Lviv
    year = input(' Please enter a year you would like to have a map for: ')
    position = input('Please enter your location (format: lat, long): ')
    year = int(year)
    position = list(map(float, position.strip().split(', ')))
    print('Map is generating...\nPlease wait...')
    create_map(position, year)
    print('Finished. Please have look at the map. For do that open file '
          'map.html')


if __name__ == '__main__':
    main()
