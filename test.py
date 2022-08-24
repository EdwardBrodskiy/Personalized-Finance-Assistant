from database import DataBase

db = DataBase()

df = db.get_merged()

print(df['ref'].is_unique)

dups = df.duplicated(subset=['ref'])
dups = df[df['ref'].isin(df[dups]['ref'])]
dups = dups.sort_values('ref')
print(dups)
