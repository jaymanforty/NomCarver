import sqlite3
import json


class MapPool:

    def __init__(self, name: str, maps: list = []):

        self.__name = name
        self.__maps = maps
        self.__maps_serialized = json.dumps(maps)
        self.__db_name = 'nomcarver.db'

    def __str__(self) -> str:
        return ','.join(self.__maps)

    def get_name(self) -> str:
        return self.__name

    def get_maps(self) -> list:
        return self.__maps

    def create(self) -> None:
        """Insert data into the database"""
        conn = sqlite3.connect(self.__db_name)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO map_pools VALUES (?, ?)""", (self.__name, self.__maps_serialized))
        conn.commit()
        conn.close()
        return True

    def update_maps(self) -> None:
        """Update maps in the database"""
        conn = sqlite3.connect(self.__db_name)
        cursor = conn.cursor()
        cursor.execute("""UPDATE map_pools SET MAPS = :maps 
                        WHERE MAP_POOL_NAME = :map_pool_name""", {'maps': self.__maps_serialized, 'map_pool_name': self.__name})
        conn.commit()
        conn.close()
        return True

    def load(self) -> None:
        """Load map pool data from database"""
        conn = sqlite3.connect(self.__db_name)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM map_pools WHERE MAP_POOL_NAME = :name""", {'name': self.__name})
        data = cursor.fetchone()
        self.__maps = json.loads(data[1])