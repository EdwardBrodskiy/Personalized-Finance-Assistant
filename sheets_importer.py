import pandas as pd
import numpy as np
from database import DataBase
import logging


def main():
    existence = pd.read_csv('sheets_ingest/Spending - Tax.csv', usecols=['Date', 'Who', 'Amount'])
    existence['Sub Account'] = pd.Series('existence', index=range(len(existence)))
    existence = existence.astype({'Date': np.datetime64, 'Who': 'category', 'Amount': np.float64, 'Sub Account': 'category'})

    life = pd.read_csv('sheets_ingest/Spending - Personal.csv', usecols=['Date', 'Who', 'What', 'Description', 'Amount', 'Running Total'])
    life['Sub Account'] = pd.Series('life', index=range(len(life)))
    life = life.astype(
        {'Date': np.datetime64, 'Who': 'category', 'What': 'category', 'Description': 'string', 'Amount': np.float64,
         'Running Total': np.float64,
         'Sub Account': 'category'})

    ingest = pd.concat([existence, life], sort=False, ignore_index=True)
    ingest['ref2'] = ingest.index

    logging.info(f'Labeled entries: {len(ingest)}')
    db = DataBase()
    database = db.get_database()

    database['ref'] = database.index

    # merge exact

    joined = database.merge(ingest, left_on=['Date', 'Value'], right_on=['Date', 'Amount'], how='outer', indicator=True)

    # save the successful ones

    good = joined[joined['_merge'] == 'both']
    good = good.rename(columns={'Description_y': 'Description'})
    good = good.sort_values('Date')

    # remove cross over duplicates

    # get the list of all duplicate entries
    dups = good.duplicated(subset=['ref2'])
    dups = good[good['ref2'].isin(good[dups]['ref2'])]
    dups = dups.sort_values('ref2')[['ref', 'ref2']]

    preserved_left, preserved_right = set(), set()
    to_remove = []
    for index, row in dups.iterrows():
        ref = row['ref']
        ref2 = row['ref2']
        if ref in preserved_left or ref2 in preserved_right:
            to_remove.append(index)
        else:
            preserved_left.add(ref)
            preserved_right.add(ref2)

    good = good.drop(index=to_remove)

    labeled_cols = ['ref', 'Who', 'What', 'Description', 'Amount', 'Sub Account']
    good = good[labeled_cols]

    # extract left and right orphans
    bad = joined[joined['_merge'] == 'right_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

    non_labeled = joined[joined['_merge'] == 'left_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

    # Try loose join on amount

    bad['_merge_amount'] = np.round(bad['Amount'] * 10).astype(int)
    non_labeled['_merge_value'] = np.round(non_labeled['Value'] * 10).astype(int)
    loose_joined = non_labeled.merge(bad, left_on=['Date', '_merge_value'], right_on=['Date', '_merge_amount'], how='outer', indicator=True)

    # clean loose join

    loose_good = loose_joined[loose_joined['_merge'] == 'both']
    loose_good = loose_good.rename(columns={'Description_y': 'Description'})
    loose_good = loose_good[labeled_cols]
    loose_good = loose_good.rename(columns={'Value': 'Amount'})

    # join with the final and save

    final = pd.concat([good, loose_good], ignore_index=True)
    logging.info(f'Final entries: {len(final)}')
    final['ref'] = final['ref'].astype(np.int64)
    db.add_to_merged(final)

    # extract left and right orphans again

    bad = loose_joined[loose_joined['_merge'] == 'right_only'].dropna(axis=1, how='all').drop('_merge', axis=1)

    logging.info(f'Bad entries: {len(bad)}')
    bad.to_csv('display_files/un_matched_labels_sheets.csv')

    non_labeled = loose_joined[loose_joined['_merge'] == 'left_only'].dropna(axis=1, how='all').drop('_merge', axis=1)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    main()
