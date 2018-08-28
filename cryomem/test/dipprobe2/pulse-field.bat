cryomem dipprobe2 set_device B --config MJJ.yaml --val1 0 --val2 %1
ping localhost -n 6 >NUL
cryomem dipprobe2 set_device B --config MJJ.yaml --val1 %1 --val2 0