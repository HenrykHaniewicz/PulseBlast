import os
from astropy.io import fits

dir = "/Volumes/Henryk_Data/PSR_J1829+2456/cal/cont/"

individual_dicts = []


for file in os.listdir( dir ):

    #print(file)

    fileF = dir + file

    try:
        hdul = fits.open( fileF )
    except OSError:
        print( "File {} did not match ASCII signature required for a fits file".format( file ) )
        continue

    # Get the frequency band used in the observation.
    try:
        frontend = hdul[0].header[ 'FRONTEND' ]
    except OSError:
        print( "Could not find any frontend information in file {}".format( file ) )
        hdul.close()
        continue

    # Get the observation mode.
    try:
        obs = hdul[0].header[ 'OBS_MODE' ]
    except OSError:
        print( "Could not find any observation mode information in file {}".format( file ) )
        hdul.close()
        continue

    # Get the start MJD
    try:
        cal_mjd = hdul[0].header[ 'STT_IMJD' ]
    except OSError:
        print( "Could not find any MJD information in file {}".format( file ) )
        hdul.close()
        continue


    # Get the cal mode.
    try:
        ra = hdul[0].header[ 'RA' ]
    except OSError:
        print( "Could not find any RA information in file {}".format( file ) )
        hdul.close()
        continue

    hdul.close()

    if obs == 'CAL':

        if ra == '14:45:16.465':
            cal_mode = 'ON'
        else:
            cal_mode = 'OFF'

        individual_dicts.append({ "FILE": file, "MODE": cal_mode, "FE": frontend, "MJD": cal_mjd })

    else:
        continue


for dict1 in individual_dicts:
    for dict2 in individual_dicts:
        if (dict1.MJD == dict2.MJD) and (dict1.FE == dict2.FE) and (dict1.MODE != dict2.MODE):

            # Determine which dict mode is the ON mode and set on_file to dict.FILE
            on_file =

            new_dict = { "ON":  }
