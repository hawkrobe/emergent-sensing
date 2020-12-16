
in.dir = '~/Desktop/light-fields/'
fields = c('0-2en01','1-2en01','2-2en01','3-2en01')

for(field in fields) {
    for(i in 0:2879) {
        
        in.file = paste(in.dir, field, '/csv/t', i, '.csv', sep ='')
        t = formatC(i, width = 4, format = "d", flag = "0")
        out.file = paste(in.dir, field, '/images/pos', t, '.png', sep ='')
        data = read.csv(in.file, header=F)
        png(out.file)
        image(as.matrix(data))
        dev.off()
        
    }

}
