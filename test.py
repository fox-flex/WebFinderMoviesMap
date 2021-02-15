import pandas as pd
from geopy.geocoders import Nominatim

df = pd.DataFrame({'test': [1, 2, 3, 4],
                   'asaa': [4, 5, 6, 7]}, index=['a', 'b', 'c', 'd'])


for line in df:
    print(line)

# print(df)
# print(df['test'])
# df.a = {'test': 2, 'asaa': 4}
# print(df)
# print(df.index[df['test'] == 5][0])
# geolocator = Nominatim(user_agent="super_puper_extra_important_request")


# def get_country(row):
#     pos = str(row[0]) + ', ' + str(row[1])
#     country = geolocator.reverse(pos, timeout=10, exactly_one=True).raw
#     country = country['address']['country']
#     print(country)
#
#
# get_country([52.509669, 13.376294])
#
#
# from haversine import haversine
#
#
# a = (49.4871968, 31.2718321)
# b = (48.379433, 31.16558)
#
# print(haversine(a, b))
