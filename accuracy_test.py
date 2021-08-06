import LatLon23
import math

hydrophone_lat = math.radians(45.33964286766197)
hydrophone_lon = math.radians(-64.38384867230519)
hydrophone_lat_lon = LatLon23.LatLon(LatLon23.Latitude(45.33964286766197), LatLon23.Longitude(-64.38384867230519))

def format_coord(coord):
    return f'{int(coord.degree)}°{int(abs(coord.minute))}\'{abs(coord.second):.3f} {coord.get_hemisphere()}'

def format_latlon(latlon):
    return f'{format_coord(latlon.lat)}, {format_coord(latlon.lon)}'.replace("-", "") # - is handled by displaying the hemisphere

# 45.35133835167251, -64.38481315165497
# calculates latitude and longitude based on an offset from a known location
# source: http://www.edwilliams.org/avform147.htm#LL
def offset_coordinates(lat1, lon1, d, tc):
    metre_to_nm_multiplier = 1 / 1852
    d = d * metre_to_nm_multiplier * math.pi / (180 * 60)

    lat = math.asin(math.sin(lat1)*math.cos(d)+math.cos(lat1)*math.sin(d)*math.cos(tc))
    dlon = math.atan2(math.sin(tc)*math.sin(d)*math.cos(lat1),math.cos(d)-math.sin(lat1)*math.sin(lat))
    lon = ((lon1 - dlon + math.pi) % (2 * math.pi)) - math.pi
    return (math.degrees(lat), math.degrees(lon))


def percent_error(expected, actual):
    return (actual - expected) / expected * 100

r = 1000

# theta = 90
for theta in range(360):
    actual = offset_coordinates(hydrophone_lat, hydrophone_lon, r, math.radians(theta))
    expected = hydrophone_lat_lon.offset(-theta, r / 1000)

    lat_err = percent_error(expected.lat.decimal_degree, actual[0])
    lon_err = percent_error(expected.lon.decimal_degree, actual[1])

    print(f'{theta}, {expected.lat.decimal_degree}, {expected.lon.decimal_degree}, {actual[0]}, {actual[1]}, {lat_err}, {lon_err}')
    # print(f'{theta}, {lat_err}, {lon_err}')
    # print(f'{lon_err}')