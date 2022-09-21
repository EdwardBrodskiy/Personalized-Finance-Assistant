from database import DataBase
import pandas as pd
import matplotlib.pyplot as plt


def main():
    sub_accounts()
    cats()
    plt.show()


def sub_accounts():
    full = get_joined()
    for account in ('existence', 'life', 'cash'):
        data = full[full['Sub Account'] == account]
        plt.plot(data['Date'], data['Value'].cumsum(), label=account)
    plt.plot(full['Date'], full['Balance'], label='Real')
    plt.plot(full['Date'], full['Amount'].cumsum(), label='caclulated')
    plt.legend(loc="upper left")


def cats():
    full = get_joined()
    full = full.groupby('What').sum()
    spending = full[full['Amount'] < 0] * -1

    income = full[full['Amount'] > 0]
    print(full)
    spending.plot.pie(y='Amount')
    income.plot.pie(y='Amount')


def get_joined():
    db = DataBase()
    data = db.get_database()
    merged = db.get_merged()
    return data.merge(merged, on='ref')


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 300)
    main()
