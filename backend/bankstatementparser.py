import sys 
import math
import re

import pandas as pd 

from datetime import datetime as dt

filename = sys.argv[1]
type = sys.argv[2]
bank = sys.argv[3]
if type == 'savings':
    if bank == 'discover':
        df = pd.read_csv(filename)
        for index, row in df.iterrows():
            desc = row['Transaction Description']
            category = math.nan
            amount = 0

            row['Transaction Date'] = dt.strptime(row['Transaction Date'], '%m/%d/%y').strftime('%m-%d-%Y')

            if row['Transaction Type'] == 'Debit':
                row['Transaction Type'] = 'Expense'
                amount = float(row['Debit'].replace('$', '').replace(',', ''))
            else:
                row['Transaction Type'] = 'Income'
                amount = float(row['Credit'].replace('$', '').replace(',', ''))

            if row['Transaction Type'] == 'Income':
                if re.search(r'interest', desc, re.IGNORECASE):
                    category = 'Interest'
                elif re.search(r'deposit.*dda to dda', desc, re.IGNORECASE):
                    category = 'Salary'
                elif re.search(r'acctverify', desc, re.IGNORECASE):
                    category = 'Other'
            else:
                if re.search(r'acctverify', desc, re.IGNORECASE):
                    category = 'Other'
                
            print(row['Transaction Date'], amount, row['Transaction Type'], category, row['Transaction Description'])
elif type == 'checking':
    if bank == 'wellsFargo':
        df = pd.read_csv(filename)
        if 'Date' not in df.columns:
            headers = ['Date', 'Amount', 'Type', 'Category', 'Description']
            df.to_csv(filename, header=headers, index=False)
            df = pd.read_csv(filename)

        for index, row in df.iterrows():
            amount = float(row['Amount'])
            desc = row['Description']

            row['Date'] = dt.strptime(row['Date'], '%m/%d/%y').strftime('%m-%d-%Y')
            row['Amount'] = float(row['Amount'])

            if row['Amount'] < 0:
                row['Type'] = 'Expense'
            else:
                row['Type'] = 'Income'

            if row['Type'] == 'Income':
                if re.search(r'pay|salary', desc, re.IGNORECASE):
                    row['Category'] = 'Salary'
                elif re.search(r'from sombreros|zelle|transfer|irs.*tax', desc, re.IGNORECASE):
                    row['Category'] = 'Gift'
            else:
                if re.search(r'recurring payment|mojang|nintendo', desc, re.IGNORECASE):
                    row['Category'] = 'Subscription'
                elif re.search(r'recurring transfer', desc, re.IGNORECASE):
                    row['Category'] = 'Savings'
                elif re.search(r'FID BKG SVC LLC MONEYLINE', desc, re.IGNORECASE):
                    row['Category'] = 'Investments'
                elif re.search(r'kindercare', desc, re.IGNORECASE):
                    row['Category'] = 'Childcare'
                elif re.search(r'zelle to.*lucie', desc, re.IGNORECASE):
                    row['Category'] = 'Gifts'
                
            print(row['Date'], abs(row['Amount']), row['Type'], row['Category'], row['Description'])

