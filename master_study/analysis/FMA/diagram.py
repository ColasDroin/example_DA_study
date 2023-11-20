import glob
import itertools
import os
from fractions import Fraction

import matplotlib.animation as mplAnim
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.special as sciSpec
from matplotlib.colors import BoundaryNorm


# ==================================================================================================
# --- Functions
# ==================================================================================================
def farey(order):
    # Create array of (value,numerator,denominator)
    allFracts = [(0, 0, 1)] + [
        (m / k,) + Fraction(f"{m}/{k}").as_integer_ratio()
        for k in range(1, order + 1)
        for m in range(1, k + 1)
    ]
    uniqueFraq = np.array(list(set(allFracts)))
    # sort by value (1st columns) and return
    return list(uniqueFraq[np.argsort(uniqueFraq[:, 0]), 1:].astype(int))


def resonance_df(order):
    """Returns a dataframe with the information of resonance lines up to a given order"""
    resonances = []
    nodes = farey(int(order))
    for node_i in nodes:
        h, k = node_i  # Node h/k on the axes
        for node_j in nodes:
            p, q = node_j
            b = float(k * p)  # Resonance line a*Qx + b*Qy = c (linked to p/q)
            if b > 0:
                a, c = float(q - k * p), float(p * h)

                # Resonance lines from a*Qx + b*Qy = c
                # Qy = c/b - a/b*Qx
                # Qy = c/b + a/b*Qx
                # Qx = c/b - a/b*Qy     -> Qy = -(Qx - c/b)*b/a      if a!=0 else Qx = c/b, Qy = [0,1]
                # Qx = c/b + a/b*Qy     -> Qy =  (Qx - c/b)*b/a      if a!=0 else Qx = c/b, Qy = [0,1]
                # Qx = c/b - a/b*(1-Qy) -> Qy =  (Qx - (c-a)/b)*b/a  if a!=0 else Qx = c/b, Qy = [0,1]
                # Qx = c/b + a/b*(1-Qy) -> Qy = -(Qx - (c+a)/b)*b/a  if a!=0 else Qx = c/b, Qy = [0,1]

                if a != 0:
                    slopes = [-a / b, a / b, -b / a, b / a, b / a, -b / a]
                    y0s = [c / b, c / b, c / a, -c / a, -(c - a) / a, (c + a) / a]
                    x0s = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                else:
                    slopes = [-a / b, a / b, np.inf]
                    y0s = [c / b, c / b, np.nan]
                    x0s = [np.nan, np.nan, c / b]

                for slope, y0, x0 in zip(slopes, y0s, x0s):
                    # Create unique ID to later eliminate duplicates
                    if slope != np.inf:
                        slope_int = Fraction(str(slope)).limit_denominator(20).as_integer_ratio()
                        y0_int = Fraction(str(y0)).limit_denominator(20).as_integer_ratio()
                        ID = slope_int + y0_int
                    else:
                        ID = (np.inf, np.inf) + Fraction(str(x0)).limit_denominator(
                            20
                        ).as_integer_ratio()

                    resonances.append(
                        {"ID": ID, "Order": int(a + b), "slope": slope, "y0": y0, "x0": x0}
                    )

            if q == k and p == 1:
                break

    resonances = pd.DataFrame(resonances)
    resonances = resonances.drop_duplicates(subset="ID").reset_index(drop=True)
    return resonances


#############################################################
# WORKING DIAGRAM


def _isLineInside(a, b, x_range, y_range, tol=0):
    """Assumes y = ax+b and finds if line goes inside the ROI"""
    x1, x2 = np.sort(x_range)
    y1, y2 = np.sort(y_range)
    tol = np.abs(tol)

    xi1 = (y1 - b) / a if a != 0 else 0
    xi2 = (y2 - b) / a if a != 0 else 0

    yi1 = a * x1 + b
    yi2 = a * x2 + b

    return (
        (x1 - tol <= xi1 <= x2 + tol)
        or (x1 - tol <= xi2 <= x2 + tol)
        or (y1 - tol <= yi1 <= y2 + tol)
        or (y1 - tol <= yi2 <= y2 + tol)
    )


def _plot_resonance_lines(df, Qx_range, Qy_range, ROI_tol=1e-3, offset=[0, 0], **kwargs):
    """Plots all resonance lines contained in a dataframe, provided by BBStudies.Physics.Resonances.resonance_df
    -> Filters out the lines that do not enter the ROI defined by Qx_range,Qy_range"""

    options = {"color": "k", "alpha": 0.15}
    options.update(kwargs)

    if "label" in options.keys():
        _label = options.pop("label")
        plt.plot([np.nan], [np.nan], label=_label, **options)

    for _, line in df.iterrows():

        # Non-vertical lines
        if line["slope"] != np.inf:
            # Skip if line not in ROI
            if not _isLineInside(line["slope"], line["y0"], Qx_range, Qy_range, tol=ROI_tol):
                continue

            xVec = np.array(Qx_range)
            yVec = line["slope"] * xVec + line["y0"]

        # Vertical line
        else:
            # Skip if line not in ROI
            if not (Qx_range[0] <= line["x0"] <= Qx_range[1]):
                continue

            xVec = line["x0"] * np.ones(2)
            yVec = np.array(Qy_range)

        # Plotting if in ROI
        plt.plot(xVec + offset[0], yVec + offset[1], **options)


def workingDiagram(Qx_range=[0, 1], Qy_range=[0, 1], order=6, offset=[0, 0], **kwargs):

    if not isinstance(order, (list, type(np.array([])))):
        # Regular, full working diagram
        resonances = resonance_df(order)
        _plot_resonance_lines(resonances, Qx_range, Qy_range, ROI_tol=1e-3, offset=offset, **kwargs)
    else:
        # Selected resonances
        resonances = resonance_df(np.max(order))
        for _ord in order:
            _plot_resonance_lines(
                resonances[resonances["Order"] == _ord],
                Qx_range,
                Qy_range,
                ROI_tol=1e-3,
                offset=offset,
                **kwargs,
            )
