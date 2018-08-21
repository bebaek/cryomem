cryomem dipprobe set_device B --config Tc.yaml --val1 0 --val2 %1
ping localhost -n 6 >NUL
cryomem dipprobe set_device B --config Tc.yaml --val1 %1 --val2 0