rad2deg <- function(rad) {(rad * 180) / (pi)}
deg2rad <- function(deg) {(deg * pi) / (180)}
angle <- function(ref.x, ref.y, other.x, other.y){
  return(rad2deg(
    (atan2(other.y-ref.y, other.x - ref.x)) 
    %% (2*pi) ))
}

dist <- function(p1.x, p1.y, p2.x, p2.y) {
  return(sqrt((p1.x-p2.x)^2 + (p1.y-p2.y)^2))
}
