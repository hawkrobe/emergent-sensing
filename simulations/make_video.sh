# e.g,
# sh scripts/make_video.sh output/predictions-emergent/spot-1-asocial-1-simulation.csv output/predictions-emergent/spot-1-asocial-1-bg.csv output/movies/

EXPPATH=$1
EXPNAME="${EXPPATH##*/}"
OUT="output/movies"
rm ${OUT}/images/*
python utils/make_images.py ${EXPPATH}simulation.csv ${EXPPATH}bg.csv ${OUT}
cat ${OUT}/images/pos*.png | ffmpeg -i - -y -framerate 8 -c:v libx264 -pix_fmt yuv420p ${OUT}/${EXPNAME}video.mp4
echo "see video at ${OUT}/${EXPNAME}video.mp4"
