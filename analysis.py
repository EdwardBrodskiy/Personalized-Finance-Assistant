from database import DataBase
import pandas as pd


def main():
    full = get_joined()
    result = full[full['Description_y'].str.contains('Model F')][['Date', 'Who', 'Description_y', 'Amount']]
    result = result[result['Who'] != 'Ebay']
    print(result)
    print(result['Amount'].sum())


def get_joined():
    db = DataBase()
    data = db.get_database()
    merged = db.get_merged()
    return data.merge(merged, on='ref')


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    main()
