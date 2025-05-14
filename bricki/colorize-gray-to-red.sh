#! /bin/sh

convert colortest.png -channel G -evaluate set 0 -channel B -evaluate set 0 -channel R -evaluate multiply 1.0 colortestred.png