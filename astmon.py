# -*- coding: utf-8 -*-
# Programa que representa los datos del Astmon
# Autor: César Husillos (versión 2, 11 Mayo 2020) 

import argparse
import os

# import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

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

def plot_data(data, out_plot, title, field_group='category_night'):
    """
    Plot information contained in input argument 'data'.

    A bit longer description.

    Args:
        data (dataframe): Input pandas dataframe. Fields are ['date', 'time', 'is_moon', 'photo_night', 'sky_bright', 'category_night'].
        out_plot (str): Path for output plot.
        title (str): Title for output plot.
        field_group (str): Field used for grouping.

    Returns:
        int: 0 - everything was fine.

    Raises:
        Exception: Type of exception depends on failed line of code.

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
    ax.legend()
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
                                     description='''This program reads, categorizes and plots data from input file. ''',
                                     epilog='''''')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument("input_file", help="Input data file")
    parser.add_argument("--output_dir",
                        action="store",
                        dest="output_dir",
                        default="./",
                        help="Output plot directory [default: %(default)s]")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Show running and progress information [default: %(default)s].")
    args = parser.parse_args()

    # Fixed field with format file
    data = pd.read_fwf(args.input_file, header=None,
                   names=['date', 'time', 'is_moon', 'photo_night', 'sky_bright'],
                   index_col=False)
    # combining two columns
    dt = data['date'] + ' ' + data['time']
    # Changing str to datetime type
    data['datetime'] = pd.to_datetime(dt, dayfirst=True)
    print(data)

    # Setting datetime as index for dataframe (useful for time series works)
    data.set_index("datetime", inplace = True)

    # classifying data: criterium photo_night
    data['category_night'] = classify(data)

    # Plotting 
    input_name = os.path.splitext(os.path.split(args.input_file)[1])[0]
    out_plot = os.path.join(args.output_dir, input_name + '.jpg')
    title = input_name
    sns.set_style("darkgrid")
    return plot_data(data, out_plot, title)


if __name__ == '__main__':
    print(main())
