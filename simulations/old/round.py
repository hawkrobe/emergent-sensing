import csv
import os

in_dir = '/home/pkrafft/couzin/output/light-fields/'
out_dir = '/home/pkrafft/couzin/output/light-fields-new/'

for name in os.listdir(in_dir): 

    if name == 'seeds.csv':
        continue
    
    print 'Parsing ' + name + '...'
    
    this_in_dir = in_dir + name
    this_out_dir = out_dir + name
    
    try:
        os.makedirs(this_out_dir)
    except:
        pass
    
    for i in range(2880):
        
        f = open(this_in_dir + '/t' + str(i) + '.csv')
        g = open(this_out_dir + '/t' + str(i) + '.csv', 'w')
        reader = csv.reader(f)
        writer = csv.writer(g)
        
        x = []
        for line in reader:
            x += [[float(x) for x in line]]
            out = map(lambda x: "{0:0.2f}".format(float(x)), line)
            writer.writerow(out)
        
        f.close()
        g.close()
