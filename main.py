"""
main module of project
"""

from random import uniform
import pandas as pd
import folium
import warnings
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
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
              path='./database/locations.list') -> pd.DataFrame:
    """
    function read data from the database and return dataset whit info
    about films
    """
    pos = str(coordinates[0]) + ', ' + str(coordinates[1])
    country = geolocator.reverse(pos, timeout=10, exactly_one=True,
                                 language='en').raw['address']['country']
    with open(path, 'r', encoding='latin-1') as f:
        for _ in range(14):
            f.readline()
        info = pd.DataFrame(columns=['place', 'films', 'coordinates',
                                     'range', 'distance'])
        for line in f.readlines()[:-1]:
            line = list(map(lambda x:x.strip(), line.split('\t')))
            line = list(filter(None, line))
            # print(line)
            name_line, place = line[:2]
            try:
                ind = name_line.index('"', 2)
            except ValueError:
                continue
            name = name_line[1:ind]
            year0 = name_line[ind + 3:ind + 7]
            if year0 != str(year) or country not in place:
                continue
            try:
                # print(0)
                print('okkkk')
                index = info.index[info['place'] == place][0]
                info['films'][index].add(name)
            except IndexError:
                try:
                    print('okk')
                    pos = place_coordinates(line[-1])
                    coord = tuple(map(float, pos['coordinates']))
                    distance = -1 * haversine(coordinates, coord)
                    info = info.append({'place':place,
                                        'films':{name},
                                        'coordinates':pos['coordinates'],
                                        'range':pos['coordinates_range'],
                                        'distance':distance},
                                       ignore_index=True)
                    # print(1)
                except AttributeError:
                    print(2)
                    continue
                except TypeError:
                    # print(3)
                    continue
    for i in info.index:
        info['films'][i] = frozenset(info['films'][i])
        info['range'][i] = tuple(info['range'][i])
    print(info)
    print('__________________')
    info = info.drop_duplicates()
    print(info)
    return info.drop_duplicates()


def create_points(data_base: pd.DataFrame, num_of_points=10) -> dict:
    """
    function return 10 most nearby places where was maiden movies
    """
    print(data_base)
    data_base = data_base.nlargest(num_of_points, 'distance')
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
    # map = folium.Map()
    # map = folium.Map(tiles="Stamen Terrain")
    # map = folium.Map(tiles='Stamen Terrain', location=[49.817545, 24.023932],
    #                  zoom_start=17)

    points = create_points(read_info(coordinates, year))
    print(points)

    map = folium.Map(location=coordinates,
                     # tiles='Hype Map',
                     zoom_start=5)

    tooltip = "Hype!"

    map.add_child(folium.Marker(location=coordinates,
                                popup="You are here!",
                                icon=folium.Icon(color='red', icon='adjust')))

    point_layer = folium.FeatureGroup(name="Films Search")

    for pos in points:
        point_layer.add_child(folium.Marker(location=pos,
                                            popup=points[pos],
                                            icon=folium.Icon(icon='cloud'),
                                            tooltip=tooltip))
        # point_layer.add_child(
        # folium.CircleMarker(location=pos, radius=10,
        #                     popup=points[pos],
        #                     # tooltip=str(nameP) + " Lat: " + str(lat) + " , Long: " + str(lng),
        #                     fill=True,  # Set fill to True
        #                     color='red',
        #                     fill_opacity=1.0)).add_to(map)
        # map.add_child(folium.Marker(location=pos,
        #                             popup=points[pos],
        #                             icon=folium.Icon()))

    map.add_child(point_layer)
    map.save('map.html')


if __name__ == '__main__':
    year = 2018
    position = '49.842957, 24.031111'  # Lviv
    # position = '47.751076, -120.740135'
    # year = input(' Please enter a year you would like to have a map for: ')
    # position = input('Please enter your location (format: lat, long): ')
    position = tuple(position.strip().split(', '))
    print('Map is generating...\nPlease wait...')
    create_map(position, year)
    print('Finished. Please have look at the map. For do that open file '
          'map.html')
