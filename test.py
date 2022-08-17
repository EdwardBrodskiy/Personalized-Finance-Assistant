import pandas as pd


dt = pd.read_csv('database/all.csv', index_col='key')

dt.to_csv('database/all.csv')

