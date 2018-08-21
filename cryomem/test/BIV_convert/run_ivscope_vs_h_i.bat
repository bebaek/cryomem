cmdaq reset
cmdaq set_field --h1 0 --h2 4000 --t 5
cmdaq set_heat --t 5
cmdaq set_sweepvolt --v 0.1

cmdaq get_vitrace_vs_h_i --h 100 -5 -150 5 100
python convert.py
rem cmdaq get_vitrace_vs_h_i --h 150 -5 -150 5 150
rem cmdaq get_vitrace_vs_h_i --h 175 -6 -150 6 175
rem cmdaq get_vitrace_vs_h_i --h 200 -7 -150 7 200
rem cmdaq get_vitrace_vs_h_i --h 215 -8 -215 8 215
cmdaq reset
