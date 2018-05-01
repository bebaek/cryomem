cmdaqiv.py reset_allsrc
cmdaqiv.py set_field h1=0 h2=4400 t=5
cmdaqiv.py set_heat t=5
cmdaqiv.py set_sweepvolt --v 0.28
rem cmdaqiv.py get_vitrace_vs_h_i h=0,13.16,223.72,-13.16,-223.72,13.16,223.72 ramp=True
cmdaqiv.py get_vitrace_vs_h_i --h 0 13.16 250.04 -13.16 -250.04 13.16 250.04 --ramp True
rem run_minorfims
