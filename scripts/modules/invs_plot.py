# Author : Vikas Chouhan (presentisgood@gmail.com)
import urllib, json
import datetime
import pandas
import argparse
import copy
import time
import sys
import smtplib
import re
import os
import math
import contextlib, warnings
from   email.mime.multipart import MIMEMultipart
from   email.mime.text import MIMEText
from   email.mime.application import MIMEApplication
import matplotlib
try:
    from  matplotlib.finance import candlestick2_ohlc, volume_overlay
except:
    from  mpl_finance import candlestick2_ohlc, volume_overlay
# entry
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import datetime as datetime
import numpy as np
from   textwrap import wrap

import pandas as pd
import datetime
from   sklearn.cluster import MeanShift, estimate_bandwidth
import copy

import plotly.plotly
from   plotly.tools import FigureFactory as FF

from   modules import invs_utils

# Switch matplotlib backend
matplotlib.pyplot.switch_backend('agg')

####################################################
# PLOTTING FUNCTIONS
#
def gen_candlestick(d_frame,
                    mode='c',
                    period_list=[],
                    title='',
                    file_name='~/tmp_plot.png',
                    plot_period=None,
                    plot_volume=True,
                    fig_ratio=None,
                    sr_list=None,
                    plot_columns=[],
                    plot_columns_subplot=[]):
    # Vars
    l_bar          = ''.join(['-']*60)
    def_fig_dim    = plt.rcParams['figure.figsize']
    def_font_size  = plt.rcParams['font.size']
    def_bars       = 50
    def_n_locs     = 6

    # Check period list
    if period_list == None:
        period_list = []
    # endif
    if sr_list == None:
        sr_list = []
    # endif

    # Make a copy
    d_frame_c_c = d_frame.copy()

    # Slice the frame which needs to be plotted
    if plot_period:
        d_frame_c    = d_frame_c_c[-plot_period:].copy()
        fig_r        = int(plot_period * 1.0/def_bars) + 1
    else:
        d_frame_c    = d_frame_c_c.copy()
        fig_r        = 1.0
    # endif

    # Check if fig_ratio is passed directly
    if fig_ratio:
        fig_ratio = float(fig_ratio)
    else:
        fig_ratio = fig_r
    # endif

    # Get date list and rmean function
    xdate     = [datetime.datetime.fromtimestamp(t) for t in d_frame_c['T']]
    rmean     = invs_utils.g_rmean_f(type='e')

    def mydate(x,pos):
        try:
            return xdate[int(x)]
        except IndexError:
            return ''
        # endtry
    # enddef
    def r_ns_tr(p_f, indx=-1, rnd=2):
        return str(round(p_f.iloc[indx], rnd))
    # enddef

    # Calculate new figure dimention
    new_fig_dim  = [ fig_ratio * x for x in def_fig_dim ]
    sub_plot_1   = 211 if len(plot_columns_subplot) > 0 else 111
    sub_plot_2   = 212 if len(plot_columns_subplot) > 0 else 111

    # Pre-processing
    fig = plt.figure(figsize=new_fig_dim)
    ax  = fig.add_subplot(sub_plot_1)
    plt.xticks(rotation = 45)
    plt.xlabel("Date")
    plt.ylabel("Price")
    #plt.title(title)

    # Title for close
    title2 = '{}:{}'.format('C', r_ns_tr(d_frame_c['c']))

    # Plot candlestick
    candlestick2_ohlc(ax, d_frame_c['o'], d_frame_c['h'], d_frame_c['l'], d_frame_c['c'], width=0.6)
    ## Plot mas
    for period_this in period_list:
        label = 'ema_' + str(period_this)
        d_s   = invs_utils.s_mode(d_frame_c, mode)
        d_frame_c[label] = rmean(d_s, period_this)
        d_frame_c.reset_index(inplace=True, drop=True)
        d_frame_c[label].plot(ax=ax)
        title2 = title2 + ' {}:{}'.format(label, r_ns_tr(d_frame_c[label]))
    # endfor
    # Add sr lines if passed
    for l_this in sr_list:
        d_frame_c[str(l_this)] = [l_this]*len(d_frame_c.index)
        d_frame_c[str(l_this)].plot(ax=ax)
    # endfor
    # Plot specific columns if passed
    for column_t in plot_columns:
        d_frame_c.reset_index(inplace=True, drop=True)
        d_frame_c[column_t].plot(ax=ax)
    # endfor
    # Plot overlay columns
    if len(plot_columns_subplot) > 0:
        ax3 = fig.add_subplot(sub_plot_2)
        for column_t in plot_columns_subplot:
            d_frame_c[column_t].reset_index(inplace=True, drop=True)
            d_frame_c[column_t].plot(ax=ax3)
        # endfor

        # Set axes
        ax3.xaxis.set_major_locator(ticker.MaxNLocator(def_n_locs * fig_ratio))
        ax3.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
    # endif
    if plot_volume:
        # Plot volume
        v_data = [ 0 if j == 'n/a' else j for j in d_frame_c['v'] ]
        ax2 = ax.twinx()
        bc = volume_overlay(ax2, d_frame_c['o'], d_frame_c['c'], v_data, colorup='g', alpha=0.2, width=0.6)
        ax2.add_collection(bc)
    # endif

    # Post-processing
    # Set grid
    plt.grid()

    # Set titles
    font_size = int(fig_ratio*def_font_size*0.7)
    plt.title(title + '\n{}\n'.format(l_bar) + '\n'.join(wrap(title2, 60)), fontsize=font_size)

    # Set axes
    ax.xaxis.set_major_locator(ticker.MaxNLocator(def_n_locs * fig_ratio))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
    fig.autofmt_xdate()
    #fig.tight_layout()

    # Plot figure
    plt.savefig(os.path.expanduser(file_name))
    # Clear plot to save memory
    plt.close()
# enddef


## This is experimental and uses plotly as the chart generation engine
## This generates candlestick chart along with support & resistance lines
def gen_supp_res(j_data, n_samples=200):
    data = j_data.as_matrix(columns=['c'])

    bandwidth = estimate_bandwidth(data, quantile=0.1, n_samples=n_samples)
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(data)

    #Calculate Support/Resistance
    ml_results = []
    for k in range(len(np.unique(ms.labels_))):
        my_members = ms.labels_ == k
        values = data[my_members, 0]
        #print values

        # find the edges
        ml_results.append(min(values))
        ml_results.append(max(values))
    # endfor

    fig = FF.create_candlestick(j_data['o'], j_data['h'], j_data['l'], j_data['c'], dates=j_data.index)

    x_ax = fig.data[0]['x']
    fig_datac = fig.data[0]

    fig_copy = copy.copy(fig)
    for k in ml_results:
        fig_data_cc = {}
        fig_data_cc['y'] = [k] * len(x_ax)
        fig_data_cc['x'] = x_ax
        fig.data.append(fig_data_cc)
    # endfor

    plotly.offline.plot(fig, filename=os.path.expanduser('~/data.html'))
# enddef
