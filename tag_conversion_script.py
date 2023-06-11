import pandas as pd

import database
import structures


def main():
    db = database.DataBase()

    merged = db.get_merged()

    new_merged = merged.drop(columns=['Who', 'What', 'Sub Account'])

    new_merged['Tags'] = merged[['Who', 'What', 'Sub Account']].apply(lambda x: [i for i in x if pd.notnull(i)], axis=1)

    new_merged = new_merged.astype(new_structures.merged_types)

    new_merged.to_csv('new_merged.csv')


if __name__ == '__main__':
    main()
