ffmpeg -y -framerate 8 -i $1/images/pos%04d.png -c:v libx264 -pix_fmt yuv420p $1/video.mp4
