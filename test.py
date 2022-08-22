
from database import DataBase


db = DataBase()

df = db.get_database()

print(df['ref'].is_unique)

print(df.tail())