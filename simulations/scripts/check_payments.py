import csv, os

f = open('../../metadata/pilot-pay.csv')

reader = csv.reader(f)
reader.next()

for line in reader:
    os.system('python make_payments.py ' + line[0] + ' ' + line[1])
