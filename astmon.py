# -*- coding: utf-8 -*-
# Programa que representa los datos del Astmon
# Autor: César Husillos (versión 2, 11 Mayo 2020) 

import argparse
import os
import copy
import calendar

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

import sqlite3

def classify(data):
    """
    Classify 'data' in three categories: bad, good or excellent night.

    It evaluates values from 'photo_night' column of input data and
    classify them following next criteria:
        * 'photo_night' < 0.5, bad night
        * 0.5 <= 'photo_night' < 0.9, good night
        * 'photo_night' >= 0.9, excellent night

    Args:
        data (pandas dataframe): Information from skyQuality network.

    Returns:
        array: Classification following 'photo_night' values.

    Raises:
        keyError: if 'photo_night' keyword doesn't exists.

    """
    # classifying data: criterium photo_night
    bad_night = data['photo_night'] < 0.5
    good_night = (data['photo_night'] >= 0.5) & (data['photo_night'] < 0.9)
    excellent_night = data['photo_night'] >= 0.9
    cat = list()
    for b, g, e in zip(bad_night, good_night, excellent_night):
        value = ''
        if b:
            value = 'bad'
        if g:
            value = 'good'
        if e:
            value = 'excellent'
        cat.append(value)
    return np.array(cat)

def time_intervals(period=None, years=None, months=None, days=None):
    """Get time interval for data to plot.
    
    Args:
        period (list): [(date_ini, date_final),...] list of tuple format.
            dates are given by "YYYY-MM-DD hh:mm:ss" string pattern.
        years (list): integer values.
        months (list): integer values in [1, 12].
        days (list): integer values in [1, 31].

        If period is given, all other parameters are ignored.
    
    Return:
        (list): of tuples. Format given by [(data_ini, date_final),...]
        
    """
    dts = []
    dts_ini = []
    dts_final = []

    if period is None and years is None and months is None and days is None:
        return dts

    if period:
        if isinstance(period, list):
            dts = [copy.deepcopy(period)]
    else:
        # Checking input types and values
        ye = mo = da = None
        if years is not None:
            ye = years
            if not isinstance(years, list):
                ye = list(years)
        if months is not None:
            mo = months
            if not isinstance(months, list):
                mo = list(months)
        if days is not None:
            da = days
            if not isinstance(days, list):
                da = list(days)
    
        # Processing dates...
        if da and mo and ye:
            dts_ini = [f"{y}-{m}-{d} 00:00:00" for d, m, y in zip(da, mo, ye)]
            dts_final = [dt.replace('00:00:00', '23:59:59') for dt in dts_ini]
        if (not da) and mo and ye:
            dts_ini = [f"{y}-{int(m):0>2d}-01 00:00:00" for m, y in zip(mo, ye)]
            month_days = [calendar.monthrange(int(y), int(m))[1] for m, y in zip(mo, ye)]
            dts_final = ["{}-{:0>2d}-{:0>2d} 23:59:59".format(y, int(m), md) for y, m, md in zip(ye, mo, month_days)]
        if  (not da) and (not mo) and ye:
            dts_ini = [f"{y}-01-01 00:00:00" for y in ye]
            dts_final = [f"{y}-12-31 23:59:59" for y in ye]

        dts = zip(dts_ini, dts_final)

    return dts

def get_data(db_file, period=None, years=None, months=None, \
    days=None, positions=None, filters=None):
    """Filter input data accesible by 'db_file' taken into account
    values given by the rest of parameters.
    
    Args:
        db_file (str): path to SQLite database file.
        period (list): time intervals given by (data_ini, date_final)
            data_ini and data_final are given by strings like 'YYYY-MM-DD hh:mm:ss'
        years (list): integer values.
        months (list): integer values in [1, 12].
        days (list): integer values in [1, 31].
        positions (list) integer values in [1, 10].
        filters (list): string values allowed are ('B', 'V', 'R', 'I').

    Returns:
        (pandas.DataFrame): Returned keywords are
            ('datetime_obs', 'is_moon', 'photo_night', 
            'sky_bright', 'position', 'filter_name')
    """

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    keywords = ['datetime_obs', 'is_moon', 'photo_night', \
        'sky_bright', 'position', 'filter_name']

    sql = f"SELECT datetime(datetime_obs, 'unixepoch') as datetime_obs, \
        {','.join(keywords[1:])} FROM measurement "
    wheres = []
    if positions:
        lpos = [f"position = '{pos}'" for pos in positions]
        wheres.append(f"({' OR '.join(lpos)})")
    if filters:
        lfilt = [f"filter_name = '{fi}'" for fi in filters]
        wheres.append(f"({' OR '.join(lfilt)})")
    intervals = []
    for t_interval in time_intervals(period, years, months, days):
        print(f"Time interval = {t_interval}")
        intervals.append(f"(datetime_obs BETWEEN strftime('%s', '{t_interval[0]}') and strftime('%s', '{t_interval[1]}'))")
    if intervals:
        wheres.append(f"({' OR '.join(intervals)})")
    
    if wheres:
        sql += " WHERE "
        sql += ' AND '.join(wheres)

    print(f"sql = {sql}")
    c.execute(sql)

    res = c.fetchall()

    df = pd.DataFrame(res, columns=keywords)

    return df

def plot_data(data, out_plot, title, field_group='category_night'):
    """
    Plot information contained in input argument 'data'.

    A bit longer description.

    Args:
        data (pandas.dataframe): Fields are 
            ['date', 'time', 'is_moon', 'photo_night', 'sky_bright', 'category_night'].
        out_plot (str): Path for output plot.
        title (str): Title for output plot.
        field_group (str): Field used for grouping.

    Returns:
        int: 0 - everything was fine.

    Raises:
        Exception: Exception type depends on failed line of code.

    """
    # Grouping dataframe
    groups = data.groupby(field_group)

    # Plotting with pandas
    fig, ax = plt.subplots()
    # Datetime format
    locator = mdates.AutoDateLocator(minticks=3, maxticks=12)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    for name, group in groups:
        ax.plot(group.sky_bright, marker='o', linestyle='', ms=5, label=name)
    ax.legend(loc="lower left")
    ax.set_title(title)
    ax.set_ylim([17,23])
    ax.set_xlabel('Datetime')
    ax.set_ylabel('Magnitude')
#    ax.grid()

    plt.show()
    # saving plot
    plt.savefig(out_plot, dpi=200)
    # closing plot
    plt.close()

    return 0

def main():
    parser = argparse.ArgumentParser(prog='astmon.py',
                                     conflict_handler='resolve',
                                     description='''It plots data from database SQLite file. 
                                     - period: date_ini date_final as strings with format "YYYY-MM-DD hh:mm:ss"
                                         If period is given, 'years', 'months' and 'days' parameters are ignored.
                                     - If 'filters' are empty, every filters are plotted.
                                     - If no 'positions' are given, all values are plotted.
                                     
                                      ''',
                                     epilog='''Use examples:
                                     Query in one time period and B, V filters
                                         python astmon.py --period '2020-03-01 00:00:00' '2020-04-15 23:59:59' --filters B V -v astmonDB.db

                                     Query in one time period, filters B and V, and positions 3, 4 and 5 
                                     python astmon.py --period '2020-03-01 00:00:00' '2020-04-15 23:59:59' --filters B V  --positions 3 4 5 -v astmonDB.db

                                     Query for 2 full years, all filters and all positions
                                     python astmon.py --years 2020 2021 -v astmonDB.db

                                     Query for one month in two years, all filters and all positions
                                     python astmon.py --years 2020 2021 --months 4 -v astmonDB.db
          
''')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument("db_file", help="SQLite file database path")
    parser.add_argument("--output_plot_dir",
                        action="store",
                        dest="output_plot_dir",
                        default="./",
                        help="Output plot directory [default: %(default)s]")
    parser.add_argument("--period",
                        action="store",
                        nargs="+", 
                        default=[],
                        dest="period",
                        help="Datetime period (init, final) with 'init' and 'final' format: YYYY-MM-DD hh:mm:ss  [default: %(default)s]")
    parser.add_argument("--years",
                        nargs="+", 
                        default=[],
                        action="store",
                        dest="years",
                        help="Input list of years for plotting [default: %(default)s]")
    parser.add_argument("--months",
                        nargs="+", 
                        default=[],
                        action="store",
                        dest="months",
                        help="Numerical list of months to plot (allowed values: [1, 12]) (1-January,..., 12-december) [default: %(default)s]")
    parser.add_argument("--days",
                        nargs="+", 
                        default=[],
                        action="store",
                        dest="days",
                        help="Numerical list of days to plot (allowed values: [1, 31]) [default: %(default)s]")
    parser.add_argument("--positions",
                        nargs="+", 
                        default=[],
                        action="store",
                        dest="positions",
                        help="Numerical list of positions for plotting (allowed values: [1, 10]) [default: %(default)s]")
    parser.add_argument("--filters",
                        nargs="+", 
                        default=[],
                        action="store",
                        dest="filters",
                        help="List of filter names to plot (allowed values: ('B', 'V', 'R', 'I') [default: %(default)s]")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Show running and progress information [default: %(default)s].")
    args = parser.parse_args()

    # args = vars(parser.parse_args())
    print(args)

    # return 2

    data = get_data(args.db_file, args.period, args.years, args.months, \
        args.days, args.positions, args.filters)

    if len(data.index) == 0:
        print("WARNING: No data registered for these parameters")
        return 1

    class_data = classify(data)

    data['category_night'] = class_data

    print(data.info())
    print(data.head())
    # return 1

    # Changing str to datetime type
    data['datetime'] = pd.to_datetime(data['datetime_obs'], dayfirst=True)
    print(data)

    print(f"Included filters = {np.unique(data['filter_name'].values)}")
    print(f"Included positions = {np.unique(data['position'].values)}")

    # Setting datetime as index for dataframe (useful for time series works)
    data.set_index("datetime", inplace = True)

    # classifying data: criterium photo_night
    data['category_night'] = classify(data)

    # Plotting 
    # input_name = os.path.splitext(os.path.split(args.input_file)[1])[0]
    input_name = 'sky_measures'
    if args.positions:
        input_name += f"_positions-{','.join(args.filters)}"
    else:
        input_name += "_positions-all"

    if args.filters:
        input_name += f"_filters-{','.join(args.filters)}"
    else:
        input_name += "_filters-all"

    out_plot = os.path.join(args.output_plot_dir, input_name + '.jpg')
    title = input_name
    sns.set_style("darkgrid")
    return plot_data(data, out_plot, title)


if __name__ == '__main__':
    print(main())
