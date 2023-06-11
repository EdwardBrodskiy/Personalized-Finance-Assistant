import database
from classifier.tag_rules_parser import rule_to_selector


def main():
    db = database.DataBase()

    merged = db.get_merged()

    automated = [
        "TV Licensing",
        "British Gas",
        "Council Tax",
        "Thames Water",
        "Travel",
        "VPN",
        "Food Shop",
        "Food Venue",
        "ISP",
        "Fencing",
        "Other Service"
    ]

    selector = rule_to_selector('Any', automated)(merged['Tags'])

    merged.loc[selector, 'Tags'] = merged.loc[selector, 'Tags'].apply(
        lambda x: x + ['Automatic'] if type(x) is list else ['Automatic'])

    merged.to_csv('new_merged.csv')


if __name__ == '__main__':
    main()
