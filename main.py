"""
main module of project
"""

from random import uniform
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from haversine import haversine, Unit


geolocator = Nominatim(user_agent="super_puper_extra_important_request")


def place_coordinates(name: str):
    try:
        info = geolocator.geocode(name).raw

        return {'coordinates': (info['lat'], info['lon']),
                'coordinates_range': info['boundingbox']}
    except AttributeError:
        pass


def read_info(path='./database/locations.list', year=2015,
              coordinates=(48.379433, 31.16558)):
    pos = str(coordinates[0]) + ', ' + str(coordinates[1])
    country = geolocator.reverse(pos, timeout=10, exactly_one=True,
                                 language='en').raw['address']['country']
    with open(path, 'r', encoding='latin-1') as f:
        for _ in range(14):
            f.readline()
        info = pd.DataFrame(columns=['place', 'films', 'coordinates',
                                     'range', 'distance'])
        for line in f.readlines()[:-1]:
            line = list(map(lambda x: x.strip(), line.split('\t')))
            line = list(filter(None, line))
            name_line, place = line[:2]
            try:
                ind = name_line.index('"', 2)
            except ValueError:
                continue
            name = name_line[1:ind]
            year0 = name_line[ind+3:ind+7]
            if year0 != str(year) or country not in place:
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
    for i in info.index:
        info['films'][i] = frozenset(info['films'][i])
        info['range'][i] = tuple(info['range'][i])
    return info.drop_duplicates()


a = read_info()
# # print(a)
# # print(len(a))
# print(a['range'])
# print(a['coordinates'])


def create_points(data_base: pd.DataFrame, num_of_points=10) -> dict:
    data_base = data_base.nlargest(num_of_points, 'distance')
    points = {}
    i = 0
    num_points = 0
    while num_points < num_of_points:
        if len(data_base['films'][i]) == 1:
            points[data_base['coordinates'][i]], *_ = data_base['films'][i]
            num_points += 1
        else:
            for name in data_base['films'][i]:
                coord = list(map(float, data_base['range'][i]))
                # print(data_base['range'][i][:2])
                # print(data_base['range'][i][2:])
                coord1 = uniform(*coord[:2])
                coord2 = uniform(*coord[2:])
                points[(coord1, coord2)] = name
                num_points += 1
                if num_points == num_of_points:
                    break
        i += 1
    return points


print(create_points(a))


def create_map(coordinates: tuple):
    # map = folium.Map()
    # map = folium.Map(tiles="Stamen Terrain")
    # map = folium.Map(tiles='Stamen Terrain', location=[49.817545, 24.023932],
    #                  zoom_start=17)

    map = folium.Map(tiles='Stamen Terrain', location=coordinates,
                     zoom_start=17)

    map.add_child(folium.Marker(location=[49.817545, 24.023932],
                                popup="Хіба я тут!",
                                icon=folium.Icon()))

    map.save('map.html')


if __name__ == '__main__':
    pass
