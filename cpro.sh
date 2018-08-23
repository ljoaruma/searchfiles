#!/bin/sh

 #kernprof -l -v test_enrty.py > ../profile_$(git describe --tags)_$(date +%Y%m%d_%H%M%S).txt
REPORT_NAME=./profile_report/report_$(date +%Y%m%d_%H%M%S)_$(git describe --tags)_cprofile.txt
rm -f sample_db.sqlite

python -m cProfile test_enrty.py > $REPORT_NAME
python -m cProfile test_enrty.py >> $REPORT_NAME
python -m cProfile test_enrty.py >> $REPORT_NAME

