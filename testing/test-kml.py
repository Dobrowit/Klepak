from shapely.geometry import Point, Polygon
from fastkml import kml

# Wczytaj plik KML
def load_polygon_from_kml(kml_file_path):
    with open(kml_file_path, 'rt', encoding='utf-8') as f:
        doc = f.read()

    # Usunięcie deklaracji kodowania z początku pliku
    doc = doc.replace('<?xml version="1.0" encoding="UTF-8"?>', '')

    k = kml.KML()
    k.from_string(doc)

    # Zakładamy, że plik KML zawiera tylko jeden placemark z polygonem
    # W razie potrzeby możesz dostosować tę część, aby obsłużyć wiele elementów
    placemarks = list(k.features())
    for placemark in placemarks:
        for feature in placemark.features():
            if isinstance(feature.geometry, Polygon):
                return feature.geometry

# Sprawdzanie czy pkt jest w obszarze gminy
def is_point_in_polygon(latitude, longitude, polygon):
    point = Point(longitude, latitude)  # Shapely używa formatu (longitude, latitude)
    return polygon.contains(point)

# Sprawdzanie czy jest w strefie
polygon = load_polygon_from_kml("c:/PYTHON/klepak-git/Klepak/geo/gmina.kml")
latitude = 54.757800
longitude = 17.561000

if polygon:
    is_within_polygon = is_point_in_polygon(latitude, longitude, polygon)
    if not is_within_polygon:
        print("Punkt znajduje się poza obsługiwanym obszarem!")
else:
    print("Nie udało się załadować wielokąta z pliku KML.")
    print("Błąd serwera przy sprawdzaniu strefy!")
