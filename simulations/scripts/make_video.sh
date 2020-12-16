#
# e.g,
# sh make_video.sh ../../out/experiment-2015-01-25-4/games/ 2015-01-25-21-37-9-713_8_3-2en01_33100416185 /Users/peter/Desktop/light-fields/3-2en01/ /Users/peter/Desktop/videos/
#

python make_images.py $1 $2 $3 $4 $5
sh to_video.sh $4/$2
