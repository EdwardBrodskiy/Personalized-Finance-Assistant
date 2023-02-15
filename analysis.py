from database import DataBase
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def main():
    db = DataBase()
    analysis(db)


def analysis(db):
    sub_accounts(db)
    cats(db)
    plt.show()


def sub_accounts(db):
    full = get_joined(db)
    for account in ('existence', 'life', 'cash'):
        data = full[full['Sub Account'] == account]
        plt.plot(data['Date'], data['Value'].cumsum(), label=account)
    plt.plot(full['Date'], full['Balance'], label='Real')
    plt.plot(full['Date'], full['Amount'].cumsum(), label='caclulated')
    plt.legend(loc="upper left")


def pie_absolute_value(sizes):
    def inner(val):
        a = np.round(val / 100 * sizes.sum(), 0)
        return a

    return inner


def cats(db):
    full = get_joined(db)

    # merge categories
    who_copy = full['Who'].cat.add_categories(list(full['What'].cat.categories))
    full['What'] = full['What'].cat.add_categories(list(full['Who'].cat.categories))
    # fill na values with who labels
    full['What'] = full['What'].fillna(who_copy)
    full = full.groupby('What').sum()

    charts = {
        'Spending': full[full['Amount'] < 0] * -1,
        'Income': full[full['Amount'] > 0]
    }
    for key, df in charts.items():
        df.plot.pie(y='Amount', title=key, autopct=pie_absolute_value(df['Amount']))


def get_joined(db):
    data = db.get_database()
    merged = db.get_merged()
    return data.merge(merged, on='ref')


def get_faith_bills(db):
    full = get_joined(db)
    # full['epoch_time'] = full['Date'].apply(lambda x: int(datetime.strptime(x, '%Y-%m-%d').strftime('%s')))
    # full['epoch_time'].astype(int)
    # move_in_time = int(datetime.strptime('2022-09-02', '%Y-%m-%d').strftime('%s'))
    move_in_time = pd.Timestamp('2022-09-02')
    bills = full[
        full['Who'].isin(['Council Tax', 'Thames Water', 'British Gas', 'TV Licensing']) &
        (full['Date'] > move_in_time) &
        ~(full['What'] == 'Faith')
        ]

    faith = full[
        full['Who'].isin(['Council Tax', 'Thames Water', 'British Gas', 'TV Licensing']) &
        (full['Date'] > move_in_time) &
        (full['What'] == 'Faith')
        ]
    print(bills[['ref', 'Date', 'Who', 'Amount']])

    print(faith[['ref', 'Date', 'Who', 'What', 'Description_y', 'Amount', 'Description_x']])

    total_due = bills['Amount'].sum() / 2

    total_payed = faith['Amount'].sum()

    print(f'{total_due=:.2f}\n{total_payed=}\ndifference={total_due + total_payed:.2f}')


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    main()
