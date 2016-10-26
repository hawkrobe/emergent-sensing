
cp -r data ../../out/full-$1-$2

cp -r data/exploratory ../../out/$1-exploratory-$2
cp -r data/confirmatory ../../out/$1-confirmatory-$2

cp data/log ../../out/$1-exploratory-$2/
cp data/log ../../out/$1-confirmatory-$2/

cp data/commit_num ../../out/$1-exploratory-$2/
cp data/commit_num ../../out/$1-confirmatory-$2/
