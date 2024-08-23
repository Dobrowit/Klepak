from shapely.geometry import Point, Polygon as ShapelyPolygon
from fastkml import kml
import pygeoif

def load_polygon_from_kml(kml_file_path):
    with open(kml_file_path, 'rb') as f:
        doc = f.read()

    k = kml.KML()
    k.from_string(doc)

    try:
        placemarks = list(k.features()) # Liczba placemarków: len(placemarks)

        for placemark in placemarks:
            features = list(placemark.features()) # Liczba funkcji w placemarku: len(features)

            for feature in features:
                geometry_type = type(feature.geometry) # Typ geometrii: geometry_type

                if isinstance(feature.geometry, pygeoif.geometry.Polygon):
                    # Znaleziono Polygon!
                    # Konwersja pygeoif.geometry.Polygon na shapely.geometry.Polygon
                    shapely_polygon = ShapelyPolygon(feature.geometry.exterior.coords)
                    return shapely_polygon
    except Exception as e:
        print("Błąd podczas przetwarzania pliku KML:", str(e))

    print("Nie znaleziono Polygonu.")
    return None

def is_point_in_polygon(latitude, longitude, polygon):
    point = Point(longitude, latitude)
    return polygon.contains(point)

# Sprawdzanie czy jest w strefie
polygon = load_polygon_from_kml("c:/PYTHON/klepak-git/Klepak/geo/gmina.kml")

latitude = 57
longitude = 57

#latitude = 54.757800
#longitude = 17.561000

if polygon:
    is_within_polygon = is_point_in_polygon(latitude, longitude, polygon)
    if is_within_polygon:
        print("OK")
    else:
        print("Punkt znajduje się poza obsługiwanym obszarem!")
else:
    print("Nie udało się załadować wielokąta z pliku KML.")
    print("Błąd serwera przy sprawdzaniu strefy!")
