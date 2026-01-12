# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 10:56:24 2021

@author: ChowK

Adapted from xclim's multiday_temperature_swing to also account for mean temperature thresholds
"""
import os
import xarray

from xclim.core.calendar import resample_doy
from xclim.core.units import (
    convert_units_to,
    declare_units,
    to_agg_units,
)
from xclim.indices import run_length as rl

def ftc_deep_mild(
    tasmin: xarray.DataArray,
    tasmax: xarray.DataArray,
    thresh_tasmin: str = "0 degC",
    thresh_tasmax: str = "0 degC",
    thresh_deep_mild: str = "0 degC",
    window: int = 1,
    op: str = "sum",
    freq: str = "YS"):
    r"""Statistics of consecutive diurnal temperature swing events.

    A diurnal swing of max and min temperature event is when Tmax > thresh_tasmax and Tmin <= thresh_tasmin. This indice
    finds all days that constitute these events and computes statistics over the length and frequency of these events.
    This has been modified so that it returns both deep and mild ftcs - in retrospect, this should be revised to return only one index based on a toggle

    Parameters
    ----------
    tasmin : xarray.DataArray
      Minimum daily temperature.
    tasmax : xarray.DataArray
      Maximum daily temperature.
    thresh_tasmin : str
      The temperature threshold needed to trigger a freeze event.
    thresh_tasmax : str
      The temperature threshold needed to trigger a thaw event.
    window : int
      The minimal length of spells to be included in the statistics.
    op : {'mean', 'sum', 'max', 'min', 'std', 'count'}
      The statistical operation to use when reducing the list of spell lengths.
    freq : str
      Resampling frequency.

    Returns
    -------
    xarray.DataArray, [time]
      {freq} {op} length of diurnal temperature cycles exceeding thresholds.

    Notes
    -----
    Let :math:`TX_{i}` be the maximum temperature at day :math:`i` and :math:`TN_{i}` be
    the daily minimum temperature at day :math:`i`. Then freeze thaw spells during a given
    period are consecutive days where:

    .. math::

        TX_{i} > 0? \land TN_{i} <  0?

    This indice returns a given statistic of the found lengths, optionally dropping those shorter than the `window`
    argument. For example, `window=1` and `op='sum'` returns the same value as :py:func:`daily_freezethaw_cycles`.
    """
    thaw_threshold = convert_units_to(thresh_tasmax, tasmax)
    freeze_threshold = convert_units_to(thresh_tasmin, tasmin)
    mid_threshold = convert_units_to(thresh_deep_mild, tasmin) #same units as tasmin in this case, deg C 
    
    #gets a true or false value from all three threshold checks
    ft_mild = (tasmin <= freeze_threshold) * (tasmax > thaw_threshold) * ((tasmin+tasmax)/2 > mid_threshold)
    ft_deep = (tasmin <= freeze_threshold) * (tasmax > thaw_threshold) * ((tasmin+tasmax)/2 <= mid_threshold)
    
    #get statistics
    if op == "count":
        out_mild = ft_mild.resample(time=freq).map(
            rl.windowed_run_events, window=window, dim="time"
        )    
        out_deep = ft_deep.resample(time=freq).map(
            rl.windowed_run_events, window=window, dim="time"    
        )
    else:
        out_mild = ft_mild.resample(time=freq).map(
            rl.rle_statistics, reducer=op, window=window, dim="time"
        )    
        out_deep = ft_deep.resample(time=freq).map(
            rl.rle_statistics, reducer=op, window=window, dim="time"    
        )

    out_mild2 = to_agg_units(out_mild, tasmin, "count")
    out_mild2.attrs['units'] = 'Days'
    out_mild2.attrs['long_name'] = 'Number of Mild Freeze-Thaw Cycles'
    out_mild2.attrs['Description'] = 'Annual Number of Freeze-Thaw Cycles with tmax > 0c, tmin <= 0c, and tmean > 0c'

    out_deep2 = to_agg_units(out_deep, tasmin, "count")
    out_deep2.attrs['units'] = 'Days'
    out_deep2.attrs['long_name'] = 'Number of Deep Freeze-Thaw Cycles'
    out_deep2.attrs['Description'] = 'Annual Number of Freeze-Thaw Cycles with tmax > 0c, tmin <= 0c, and tmean <= 0c'
    
    return out_mild2, out_deep2 
    
    