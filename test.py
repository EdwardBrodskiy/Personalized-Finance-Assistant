import pandas as pd
import numpy as np
from database import DataBase
from structures import mp

from other import sep
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 300)


ingest = pd.read_csv('sheets_ingest/Spending - Tax.csv', usecols=['Date', 'Who', 'Amount'])
ingest = ingest.astype({'Date': np.datetime64, 'Who': 'string', 'Amount': np.float64})


sep()

database = DataBase.get_database()

database['ref'] = database.index

# merge exact

joined = database.merge(ingest, left_on=['Date', 'Value'], right_on=['Date', 'Amount'], how='outer', indicator=True)

# save the successful ones
good = joined[joined['_merge'] == 'both']
good = good[['Who', 'ref']]

good.to_csv('database/merged.csv')

# extract left and right orphans
bad = joined[joined['_merge'] == 'right_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

non_labeled = joined[joined['_merge'] == 'left_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

# Try loose join on amount

bad['_merge_amount'] = np.round(bad['Amount']*10).astype(int)
non_labeled['_merge_value'] = np.round(non_labeled['Value']*10).astype(int)


loose_joined = non_labeled.merge(bad, left_on=['Date', '_merge_value'], right_on=['Date', '_merge_amount'], how='outer', indicator=True)


# clean loose join
loose_good = loose_joined[loose_joined['_merge'] == 'both']
loose_good = good[['Who', 'ref']]

# extract left and right orphans again
bad = joined[joined['_merge'] == 'right_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

non_labeled = joined[joined['_merge'] == 'left_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

print(bad)

print(non_labeled)