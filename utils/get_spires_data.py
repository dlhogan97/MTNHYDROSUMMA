import os
from ftplib import FTP
import pandas as pd
import datetime as dt

def download_spires_data(
    year: int,
    months: list[str],
    product: str = "NRT",         # or "HIST"
    tile: str = "h09v05",
    destination_base: str = "~/data/spires"
):
    """
    Download SPIRES data from the CU FTP server for a given year and list of months.
    
    Parameters:
        year (int): The year of data to download (e.g., 2023)
        months (list[str]): List of 2-digit month strings to download (e.g., ["04", "05"])
        product (str): Either "NRT" or "HIST"
        tile (str): Tile identifier, e.g., "h09v05"
        destination_base (str): Base path to store data (e.g., "~/data/spires")
    """
    
    # Validate input
    assert product in ["NRT", "HIST"], "Product must be 'NRT' or 'HIST'"
    for m in months:
        assert len(m) == 2 and m.isdigit(), f"Month {m} must be a 2-digit string"

    # FTP connection info
    host_name = "dtn.rc.colorado.edu"
    ftp_user = "anonymous"
    ftp_pwd = "pwd"
    base_path = "/shares/snow-today/spires"
    sub_path = f"SPIRES_{product}_V01/{tile}"
    remote_path = f"{base_path}/{sub_path}/{year}"

    # Create date range and filter
    start_date = dt.datetime(year, 1, 1)
    end_date = dt.datetime(year, 12, 31)
    all_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    filtered_dates = all_dates[all_dates.strftime("%m").isin(months)]

    # Format filenames
    file_template = f"SPIRES_{product}_h09v05_MOD09GA061_{{date}}_V1.0.nc"
    file_names = [file_template.format(date=d.strftime("%Y%m%d")) for d in filtered_dates]

    # Create local output directory
    output_dir = os.path.expanduser(f"{destination_base}/{year}")
    os.makedirs(output_dir, exist_ok=True)

    # Connect to FTP and download files
    ftp = FTP(host_name)
    ftp.login(user=ftp_user, passwd=ftp_pwd)
    ftp.cwd(remote_path)

    for fname in file_names:
        local_path = os.path.join(output_dir, fname)
        if not os.path.exists(local_path):  # Avoid redownloading
            try:
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f"RETR {fname}", f.write)
                print(f"Downloaded: {fname}")
            except Exception as e:
                print(f"❌ Could not download {fname}: {e}")
        else:
            print(f"✔️ Already exists: {fname}")

    ftp.quit()
    print(f"All downloads complete. Check {output_dir} for files.")
    return

from pynhd import NLDI

def clip_to_basin(
    ds, gage_id
    ):
        """
        Filter the dataset for snow fraction based on a basin shapefile.
        
        Parameters:
            ds (xarray.Dataset): The dataset containing snow fraction data.
            gage_id (str): gage id number (e.g. East River: 09112500)
        
        Returns:
            xarray.Dataset: Filtered dataset with valid snow fraction data.
        """
        basin = NLDI().get_basins(gage_id)
        # write crs
        basin = basin.set_crs("EPSG:4326")  # Ensure the basin geometry has a CRS
        ds = ds.rio.write_crs(ds.crs.attrs['crs_wkt'])
        # check to make sure the crs matches between basin and ds 

        if basin.crs != ds.rio.crs:
            print("CRS mismatch! Basin GDF CRS:", basin.crs, "Dataset CRS:", ds.rio.crs)
            # reproject ds to match basin
            ds = ds.rio.reproject(basin.crs)
            print("Reprojected dataset CRS:", ds.rio.crs)
            # check that they match again
            if basin.crs != ds.rio.crs:
                raise ValueError("CRS still does not match after reprojection!")
        # clip to the basin boundary
        ds = ds.rio.clip(basin.geometry, basin.crs, drop=True)
        return ds