# Personalized Finance Assistant

This is an accounting program made to track you day to day transactions. It is able to automatically classify many of
your transactions while part labeling others and letting you fill in the details. On top of this it provides
analysis functions to view and study your use of money.

# Setting up

First make sure you are in the root of the project directory.

## Python

Optionally you may want to set up a virtual environment (recommended):

```shell
python -m venv venv
```

Activate it:

```shell
source venv/bin/activate
```

Install the required packages using the following command:

```shell
pip install -r requirements.txt
```

## Add your transactions

The program by default expects your data to be in specific folders in the project directory (you can change this
later in the "config/filepaths.json")

For now create a folder structure as follows:

program_root:

- user_data
    - input
        - 2020.csv
        - 2021.csv
        - ...

This is done in such a format as most banks only allow the download of a year of records at a time. If you wish to use
a single csv just label it a single year such as 2020.csv.

## Run the program

Run the app using the command below in your terminal:

```bash
python app.py
```

## Configuration

After running the app for the first time the program would have created a config folder. In it you will find these
files:

- **filepaths.json** : This contains the file paths for all the files the program operates on. I
  recommend making user_data a git managed folder meaning you are able to keep a history and easily back up your
  transaction data.
- **tag_rules.json** : This files is where all the automatic classification rules are defined. I recommend spending
  some time defining the rules in this file as this will save you lots of time down the line. The specifics of
  these rules are discussed in the following section.

# Classification and Tag Rules

Classification is based on a simple premiss of assigning tags based on a set of conditions. These conditions are
implemented with the use of these selectors available to you.

Special ops:

- **~** : Not operator which can be included in front of any other rule

List Selectors (Mostly for selecting based on tags):

- **Any** : takes a list returns True if any are found
- **All** : takes a list returns True if all are found

String Selectors (for columns like Description):

- **Includes** : takes a list returns True if any of the strings are contained within

Length selectors:

- **Has** : takes an integer returns equivalent of (x >= len(row_value)

## Tag Rules Format

First consider a single tag rule. Its structure is as follows.

```json
{
  "Tag to be assigned in case the condition is true": {
    "Column in the transactional data": {
      "Operation (see defined above)": [
        "Input conditions for the operation"
      ]
    }
  }
}
```

Here is an example that assigns that tag "Travel" to all rows which contain the words "Travel" or "Uber" in their
description.

```json
{
  "Travel": {
    "Description": {
      "Includes": [
        "TRAVEL",
        "UBER"
      ]
    }
  }
}
```

## Higher Tags

In some cases you may want to continue the evaluation of a row by considering the tags that have already been
assigned to it. To ensure the order of these operations and for general organisation the tag rules are placed in a list.

So most of your low level rules such as the one shown in the prior section can exist in the first group. A higher
level tags is best described by looking at the most critical high level tag which is already implemented for you.
The "Automated" tag tells the classifier that this row does not need further clarification from the user meaning it
will not be shown in the manual classification stage. Here is a reduced version of how this higher level tag is
implemented:

```json
{
  "Automatic": {
    "Tags": {
      "Any": [
        "Travel",
        "VPN",
        "Food Shop",
        "ISP",
        "Subscription"
      ]
    }
  }
}
```

The key difference is that we are now evaluating upon prior tags instead of the base rows of the input table. What
is labeled as "Automatic" is a personal decision however it is best used for transactions that don't need further
clarification such as examples described by the tags above.
