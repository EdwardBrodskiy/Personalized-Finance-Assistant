from database import DataBase
import pandas as pd


def main():
    full = get_joined()
    print(full[full['What'] == 'Faith'][['Date', 'Who', 'Description_y', 'Amount']])


def get_joined():
    db = DataBase()
    data = db.get_database()
    merged = db.get_merged()
    return data.merge(merged, on='ref')


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    main()
