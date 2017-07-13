import numpy as np

def get_temperature(**kwargs):
    """Return temperature from input resistance or voltage based on
    calibration
    
    keyword arguments:
        
    """
    # Lakeshore Cernox
    if kwargs["maker"].lower == "lakeshore":
        serial = kwargs["serial"]
        coef = np.loadtxt("fit_{}.txt".format(serial))
        coeflist = list(coef)
        temperature = chevy_poly(
