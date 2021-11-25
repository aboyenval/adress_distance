"""
Calculate distance between 2 addresses
"""
import requests
import json
import time
from typing import Optional, Tuple


class DistanceCalculation:
    """
    Calculate distance between 2 addresses
    """

    def get_distance(self, adr_start: str, adr_end: str) -> str:
        '''
        Get address from gov open data, of from openstreetmap if failed
        :param adrStart: departure address
        :param adrEnd: destination_address
        :return:
            Distance if an address cannot be localized, else the distance
        '''

        ret = None

        geocode_start = self.__geocode_adress_gov(adr_start)

        # if geoloc failed, try with open street map
        if geocode_start is None:
            geocode_start = self.__geocode_adress_openstreetmap(adr_start)

        geocode_end = self.__geocode_adress_gov(adr_end)
        if geocode_end is None:
            geocode_end = self.__geocode_adress_openstreetmap(adr_end)

        # calculate routing
        if geocode_start is not None and geocode_end is not None:
            ret = self.__routage(geocode_start, geocode_end)

        return ret

    @staticmethod
    def __geocode_adress_gov(adr: str) -> Optional[Tuple]:
        """
        Geolocation using french government API
        :param adr: address to geocode
        :return:
            None if geolocation failed, else tuple with latitude and longitude
        """
        ret = None

        r = requests.get(f"https://api-adresse.data.gouv.fr/search/?q={adr}&type=housenumber&limit=1&autocomplete=1", data={})
        if r.status_code == 200:
            data_json = r.content.decode("utf-8")
            data_dict = json.loads(data_json)

            if len(data_dict['features']) > 0:
                if 'geometry' in data_dict['features'][0]:
                    if 'coordinates' in data_dict['features'][0]['geometry']:
                        lat = str(data_dict['features'][0]['geometry']['coordinates'][1])
                        lon = str(data_dict['features'][0]['geometry']['coordinates'][0])

                        ret = lat, lon

        return ret

    @staticmethod
    def __geocode_adress_openstreetmap(adr: str) -> Optional[Tuple]:
        """
        Geolocation using OpenStreetMap API
        :param adr: address to geocode
        :return:
            None if geolocation failed, else tuple with latitude and longitude
        """
        ret = None

        r = requests.get(f"https://nominatim.openstreetmap.org/search?limit=1&format=json&q={adr}", data={})
        if r.status_code == 200:
            data_json = r.content.decode("utf-8")
            data_dict = json.loads(data_json)
            if len(dict) > 0:
                if "lat" in data_dict[0] and "lon" in data_dict[0]:
                    lat = data_dict[0]['lat']
                    lon = data_dict[0]['lon']

                    ret = lat, lon

        return ret

    @staticmethod
    def __routage(coords_start: Tuple, coords_end: Tuple) -> str:
        """
        Calculate routing between 2 coordinates
        :param coords_start: departure
        :param coords_end: destination
        :return:
            None if failed, else distance
        """

        (lat_s, lon_s) = coords_start
        (lat_e, lon_e) = coords_end

        ret = None
        r = requests.get(f"https://routing.openstreetmap.de/routed-car/route/v1/driving/{lon_s},{lat_s},{lon_e},{lat_e}?overview=false&geometries=polyline&steps=true", data={})
        if r.status_code == 200:
            data_json = r.content.decode("utf-8")
            data_dict = json.loads(data_json)
            if data_dict['code'] == "Ok" and len(data_dict['routes']) > 0:
                ret = data_dict['routes'][0]['distance']

        return ret

