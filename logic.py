import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map:
    def __init__(self, database):
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return True
            return False

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city, cities.lat, cities.lng 
                            FROM users_cities 
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            return cursor.fetchall()

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT lat, lng FROM cities WHERE city=?", (city_name,))
            return cursor.fetchone()

    def create_graph(self, path, cities):
        fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.stock_img()

        for city in cities:
            name, lat, lon = city
            ax.plot(lon, lat, marker='o', color='red', markersize=5, transform=ccrs.PlateCarree())
            ax.text(lon + 1, lat, name, fontsize=8, transform=ccrs.PlateCarree())

        plt.savefig(path)
        plt.close()