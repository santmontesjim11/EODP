import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import os
import numpy as np
import matplotlib.pyplot as plt

from l1c.src.l1c import l1c
from common.io.writeToa import readToa
from common.io.readGeodetic import readGeodetic


auxdir = r"C:\Users\santi\Desktop\MSTR-2\PODT\gitt\gitttt\auxiliary"

indir = r"C:\Users\santi\Desktop\MSTR-2\PODT\EODP_TER_2021\EODP-TS-L1C\input\gm_alt100_act_150\,C:\Users\santi\Desktop\MSTR-2\PODT\EODP_TER_2021\EODP-TS-L1C\input\l1b_output"

outdir = "C:/Users/santi/Desktop/MSTR-2/PODT/EODP_TER_2021/EODP-TS-L1C/outputsanti"

myL1c = l1c(auxdir, indir, outdir)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radio terrestre [m]

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    a = (
        np.sin((lat2 - lat1) / 2)**2
        + np.cos(lat1) * np.cos(lat2)
        * np.sin((lon2 - lon1) / 2)**2
    )

    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


for band in myL1c.globalConfig.bands:
    toa = readToa(
        myL1c.l1bdir,
        myL1c.globalConfig.l1b_toa + band + ".nc"
    )

    lat, lon = readGeodetic(
        myL1c.gmdir,
        myL1c.globalConfig.gm_geoloc
    )

    myL1c.checkSize(lat, toa)

    lat_l1c, lon_l1c, toa_l1c = myL1c.l1cProjtoa(
        lat, lon, toa, band
    )

    # L1B contra L1C
    lon_borde = np.concatenate([
        lon[0, :],
        lon[1:, -1],
        lon[-1, -2::-1],
        lon[-2::-1, 0]
    ])

    lat_borde = np.concatenate([
        lat[0, :],
        lat[1:, -1],
        lat[-1, -2::-1],
        lat[-2::-1, 0]
    ])

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        lon_borde, lat_borde,
        color="red", linewidth=1
    )

    ax.scatter(
        lon.ravel(), lat.ravel(),
        s=3, color="red", label="L1B", zorder=2
    )

    ax.scatter(
        lon_l1c, lat_l1c,
        s=6, marker="x", linewidths=0.6,
        color="blue", label="L1C MGRS", zorder=3
    )

    ax.set_title(f"Projection on ground - {band}")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.grid(alpha=0.4)
    ax.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(
        os.path.join(outdir, f"grid_{band}.png"),
        dpi=150
    )
    plt.show()
    plt.close(fig)

    # Spatial Sampling Distance de L1B
    control_row = lat.shape[0] // 2
    control_column = lat.shape[1] // 2

    ssd_act = haversine(
        lat[control_row, :-1],
        lon[control_row, :-1],
        lat[control_row, 1:],
        lon[control_row, 1:]
    )

    ssd_alt = haversine(
        lat[:-1, control_column],
        lon[:-1, control_column],
        lat[1:, control_column],
        lon[1:, control_column]
    )

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].plot(
        np.arange(len(ssd_act)), ssd_act,
        color="red"
    )
    axes[0].set_title(f"L1B - Control row {control_row}")
    axes[0].set_xlabel("ACT pixel")

    axes[1].plot(
        np.arange(len(ssd_alt)), ssd_alt,
        color="blue"
    )
    axes[1].set_title(f"L1B - Control column {control_column}")
    axes[1].set_xlabel("ALT pixel")

    for ax in axes:
        ax.set_ylabel("Spatial Sampling Distance [m]")
        ax.grid(alpha=0.4)
        ax.ticklabel_format(
            axis="y", style="plain", useOffset=False
        )

    fig.suptitle(f"Spatial Sampling Distance - {band}")
    fig.tight_layout()
    fig.savefig(
        os.path.join(outdir, f"spatial_sampling_{band}.png"),
        dpi=150
    )
    plt.show()
    plt.close(fig)