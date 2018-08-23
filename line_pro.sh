#!/bin/sh

REPORT_NAME=./profile_report/report_$(date +%Y%m%d_%H%M%S)_$(git describe --tags)_cprofile.txt
rm -f sample_db.sqlite

kernprof -l -v test_enrty.py > $REPORT_NAME
kernprof -l -v test_enrty.py >> $REPORT_NAME
kernprof -l -v test_enrty.py >> $REPORT_NAME

