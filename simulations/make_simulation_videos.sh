# e.g,
# parallel --jobs 1 --colsep ',' "sh ./make_simulation_videos.sh {1}" :::: "simulation_paths.csv"

EXPPATH=$1
OUT="output/movies"
python utils/make_images.py ./output/predictions-emergent/${EXPPATH}simulation.csv ./output/predictions-emergent/${EXPPATH}bg.csv ${OUT}
ls ${OUT}/images/${EXPPATH}simulation
cat ${OUT}/images/${EXPPATH}simulation/pos*.png | ffmpeg -i - -y -framerate 8 -c:v libx264 -pix_fmt yuv420p ${OUT}/${EXPPATH}-video.mp4
echo "see video at ${OUT}/${EXPPATH}-video.mp4"
