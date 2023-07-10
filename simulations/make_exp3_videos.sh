# e.g,
# # parallel --colsep ',' "sh ./make_empirical_videos.sh {1} {2}" :::: "empirical_paths.csv"

bgid=$1
gameid=$2
OUT="output/movies"
python utils/make_images.py ../data/experiment3/processed/${gameid}.csv ~/Downloads/light-fields/${bgid} ${OUT}
cat ${OUT}/images/${gameid}/pos*.png | ffmpeg -i - -y -framerate 8 -c:v libx264 -pix_fmt yuv420p ${OUT}/${gameid}-video.mp4
echo "see video at ${OUT}/${gameid##*/}video.mp4"
