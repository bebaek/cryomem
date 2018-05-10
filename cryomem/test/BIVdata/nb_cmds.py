"""Import this from jupyter notebook and run user functions."""
import mylib, sys
import matplotlib.pyplot as plt
import pandas as pd
#from Ipython.display import display
from cryomem.analysis.fit_datafile import fit_datafile
from cryomem.analysis.build_curve import build_curve
from cryomem.common.plothyst import plothyst
import cryomem.common.datafile as datafile
from cryomem.analysis.jj_curves import airypat_easy
from cryomem.fab.wedge import Wedge

# user functions ##################################################

dbname = "results.txt"

def process_new_datafiles(datafiles, ignore):
    """Process given datafiles in the datafiles list (minus ignore).

    Example:
        datafiles = glob.glob("data/*.zip")
        ignore    = glob.glob("data/*.bad")
    """
    datafiles = mylib.pick_datafiles(datafiles, ignore)
    print("N of datafiles:", len(datafiles))

    # initialize main dataframe
    df = mylib.load_db(dbname)
    fig = plt.figure()
    for dataf in datafiles:
        try:
            exist = (mylib.add_prefix2filename(datafile, "RSJ") ==
                     df.datafile).any()
        except:
            exist = False

        # process only unregistered (new) datafile
        if not exist:
            print("Datafile:", dataf)

            # fit 1: RSJ fit
            mode = "r"
            while mode == "r":
                # subplot 1: main fit results
                data, md    = fit_datafile(dataf)   # fit IVs
                plt.subplot(121)
                plothyst(data["Bapp"], data["Icp"], "o")
                plothyst(data["Bapp"], data["Icn"], "o")

                # subplot 2: a sample IV
                data0, md0  = datafile.load_data(dataf)
                ind         = 0
                x           = data0["Iarr"][ind]
                y           = data0["Varr"][ind]
                plt.subplot(122)
                plt.plot(x, y, "o")

                # subplot 2: overlaid IV fit
                func        = md["fitfunc"]
                p = [data[key][ind] for key in ("Icp", "Icn", "Rn", "V0")]
                fitcurve = build_curve(func, x, *p)
                plt.plot(fitcurve[0], fitcurve[1], "-")

                plt.show()

                # Prompt user
                mode = input(
                    "Your choice (c: continue, d: discard, r: refit"
                    ", q: quit)? ")
                if mode == "r":
                    # get user's fit guess
                    pass
                elif mode == "q":
                    sys.exit(1)

            # fit 2: Fraunhofer pattern fit
            if mode == "c":
                mode        = "r"
                guess       = {}
                dataf2   = mylib.add_prefix2filename(dataf, "RSJ")
                while mode == "r":
                    popt, md            = fit_datafile(dataf2, **guess)
                    popt2               = [popt[key] for key in popt]
                    func, x             = md["fitfunc"], md["fitx"]
                    fitcurve            = build_curve(func, x, *popt2)
                    plothyst(data["Bapp"], data["Icp"], "o")
                    plothyst(data["Bapp"], data["Icn"], "o")
                    plt.plot(fitcurve[0], fitcurve[1], "-", lw=3)
                    #plt.pause(0.1)
                    plt.show()
                    mode = input(
                        "Your choice (c: continue, d: discard, r: refit" +
                        ", q: quit)? ")
                    if mode == "r":
                        # get user's fit guess
                        guess = {}
                        for key in ("istart", "iend", "Icp0", "Hcen0", "Hnod0"):
                            val = input(("Fit guess for {} (enter to skip)? "
                                    "").format(key))
                            try:
                                guess[key] = int(val) if key in ("istart",
                                "iend") else float(val)
                            except:
                                print("No manual input for {}.".format(key))

                    elif mode == "q":
                        sys.exit(1)

                # add to df
                if mode == "c":
                    df = df.append(pd.Series(
                        {"datafile": dataf2, "Icp": popt["Icp"],
                        "Rn": popt["Rn"], "Bcen": popt["Bcen"],
                        "Bnod": popt["Bnod"]}),
                        ignore_index=True)
    #plt.close()
    # save
    df.to_csv(dbname, index=False)
    print("Done.")

def show_BIc():
    """Plot Ic(B) from all fit files."""
    func    = airypat_easy
    df      = mylib.load_db(dbname)
    n       = len(df)
    nrow    = 3
    ncol    = int(n/nrow) + 1
    fig     = plt.figure(figsize=(20,ncol*4))

    # Loop over record
    for k in df.index:
        plt.subplot(ncol, nrow, k+1)
        rec = df.iloc[k]

        # Load and plot data
        data, md = datafile.load_data(rec.datafile)
        plothyst(data["Bapp"], data["Icp"], "o")
        plothyst(data["Bapp"], data["Icn"], "o")

        # Plot fit curve
        popt                = [rec.Icp, rec.Bcen, rec.Bnod]
        fitcurve            = build_curve(func, data["Bapp"], *popt)
        plt.plot(fitcurve[0], fitcurve[1], "-", lw=3)

        # Put down text
        plt.text(.5,1.01,rec.datafile, transform=plt.gca().transAxes, ha="center")

    plt.tight_layout()
    plt.show()

def show_thickness_dependence(dbs=["results.txt"], devspecs=[{}]):
    """Plot Ic(d) and Bcen(d).
    
    Arguments:
        dbs:        list of fit result filename/paths.
        devspecs:   list of dictionary. Define individual device series to plot.
                    Ex: [{"wafer": "B180406", "cols": ["3"], "xoffset": 0,
                    "duration": 60, "calfile": "wedge_Ni_B180329.dat",
                    "reticle": "SF1", "angle": 0}]
    """
    devspecs2   = pd.DataFrame([rec for rec in devspecs]) # makes search easier
    w           = Wedge()
    result_list = []        # thickness, Ic dataframes
    fig         = plt.figure(figsize=(20,10))

    # Loop over different measurement sets (directories)
    for db in dbs:
        df      = mylib.load_db(db)
        result  = pd.DataFrame()

        # Loop over records
        for k in df.index:
            rec = df.iloc[k]

            # Get wedge thickness
            wafer, chip, device = mylib.get_device_id(rec.datafile)
            col = chip[0]
            devspecs3 = devspecs2[(devspecs2["wafer"] == wafer) &
                    pd.Series([col in cols for cols in devspecs2["cols"]],
                        name="cols")]
            kwargs = {'calfile':    devspecs3.loc[0,"calfile"],
                    'reticle':      devspecs3.loc[0,'reticle'],
                    'chip':         chip,
                    'device':       device,
                    'angle':        devspecs3.loc[0, 'angle'],
                    "duration":     devspecs3.loc[0, 'duration']}
            d = w.get_thickness(**kwargs)
            result = result.append({'datafile': rec.datafile, 'd': d,
                'Vcp': rec.Icp*rec.Rn, 'Hcen': rec.Bcen}, ignore_index=True)

        plt.subplot(211)
        plt.plot(result.d, result.Vcp, "o", label='{}_c{}'.format(wafer, col))
        plt.subplot(212)
        plt.plot(result.d, result.Hcen, "o", label='{}_c{}'.format(wafer, col))
        result_list.append(result)

    # save and finish up
    pd.concat(result_list).to_csv("result_thickness.txt", index=False)
    plt.subplot(211)
    plt.ylabel("IcRn (V)")
    plt.subplot(212)
    plt.xlabel("Thickness (nm)")
    plt.ylabel("Bcen (Oe)")
    plt.tight_layout()
