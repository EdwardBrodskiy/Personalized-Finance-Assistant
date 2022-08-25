from database import DataBase

db = DataBase()

df = db.get_merged()

print(df[df['ref'].isna()])

