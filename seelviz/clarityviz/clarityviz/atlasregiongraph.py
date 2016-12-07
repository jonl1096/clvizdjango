#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import print_function

__author__ = 'seelviz'

from plotly.offline import download_plotlyjs
from plotly.graph_objs import *
from plotly import tools
import plotly

import os
#os.chdir('C:/Users/L/Documents/Homework/BME/Neuro Data I/Data/')

import csv,gc  # garbage memory collection :)

import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import axes3d

# from mpl_toolkits.mplot3d import axes3d
# from collections import namedtuple

import csv
import re
import matplotlib
import time
import seaborn as sns

from collections import OrderedDict

class atlasregiongraph(object):
    """Class for generating the color coded atlas region graphs"""

    def __init__(self, token, path=None):
        self._token = token
        self._path = path
        data_txt = ""
        if path == None:
            data_txt = 'output/' + token + '/' + token + '.region.csv'
            self._path = 'output/' + token
        else:
            data_txt = path + '/' + token + '.region.csv'
        self._data = np.genfromtxt(data_txt, delimiter=',', dtype='int', usecols = (0,1,2,4), names=['x','y','z','region'])

    def generate_atlas_region_graph(self, resolution, path=None, numRegions = 10):
        font = {'weight' : 'bold',
            'size'   : 18}

        matplotlib.rc('font', **font)
        thedata = self._data
        if path == None:
            thedata = self._data
        else:
        ### load data
            thedata = np.genfromtxt(self._path + '/' + self._token + '.region.csv', delimiter=',', dtype='int', usecols = (0,1,2,4), names=['x','y','z','region'])

        # Set tupleResolution to resolution input parameter
        tupleResolution = resolution;

        # EG: for Aut1367, the spacing is (0.01872, 0.01872, 0.005).
        xResolution = tupleResolution[0]
        yResolution = tupleResolution[1]
        zResolution = tupleResolution[2]
        # Now, to get the mm image size, we can multiply all x, y, z
        # to get the proper mm size when plotting.

        """Load the CSV of the ARA with CCF v2 (see here for docs:)"""
        ccf_txt = './../ccf/natureCCFOhedited.csv'

        ccf = {}
        with open(ccf_txt, 'rU') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                # row[0] is ccf atlas index, row[4] is string of full name
                ccf[row[0]] = row[4];
                # print row[0]
                # print row[4]
                # print ', '.join(row)

        """Save counts for each region into a separate CSV"""
        unique = [];

        for l in thedata:
            unique.append(l[3])

        uniqueNP = np.asarray(unique)
        allUnique = np.unique(uniqueNP)
        numRegionsA = len(allUnique)

        # Store and count the number of regions in each unique region
        dictNumElementsRegion = {}

        for i in range(numRegionsA):
            counter = 0;
            for l in thedata:
                if l[3] == allUnique[i]:
                    counter = counter + 1;
                    dictNumElementsRegion[ccf[str(l[3])]] = counter;

        region_names = dictNumElementsRegion.keys()
        number_repetitions = dictNumElementsRegion.values()

        from itertools import izip

        with open('ARA_CCF2_ds_10XCounts.csv', 'wb') as write:
            writer = csv.writer(write)
            writer.writerows(izip(region_names, number_repetitions))



        region_dict = OrderedDict()
        for l in thedata:
            trace = ccf[str(l[3])]
            # trace = 'trace' + str(l[3])
            if trace not in region_dict:
                region_dict[trace] = np.array([[l[0], l[1], l[2], l[3]]])
                # print 'yay'
            else:
                tmp = np.array([[l[0], l[1], l[2], l[3]]])
                region_dict[trace] = np.concatenate((region_dict.get(trace, np.zeros((1, 4))), tmp), axis=0)
                # print 'nay'

        current_palette = sns.color_palette("husl", numRegions)
        # print current_palette

        data = []
        for i, key in enumerate(region_dict):
            trace = region_dict[key]
            tmp_col = current_palette[i]
            tmp_col_lit = 'rgb' + str(tmp_col)
            temp = str(np.unique(trace[:, 3])).replace("[", "")
            final = temp.replace("]", "")

            trace_scatter = Scatter3d(
                x=[x * xResolution for x in trace[:, 0]],
                y=[x * yResolution for x in trace[:, 1]],
                z=[x * zResolution for x in trace[:, 2]],

                mode='markers',
                name=ccf[final],
                marker=dict(
                    size=1.2,
                    color=tmp_col_lit,  # 'purple',                # set color to an array/list of desired values
                    colorscale='Viridis',  # choose a colorscale
                    opacity=0.15
                )
            )

            data.append(trace_scatter)
            

        layout = Layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0
            ),
            paper_bgcolor='rgb(0,0,0)',
            plot_bgcolor='rgb(0,0,0)'
        )

        fig = Figure(data=data, layout=layout)
        plotly.offline.plot(fig, filename= self._path + '/' + self._token + "_region_pointcloud.html")

