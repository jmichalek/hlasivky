#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" This script 
    * calculates the ID numbers of geometricaly defined points in the simulation
      from the standard Elmer files in ./mesh/ directory and reports
      the numbers to standard output (to be included in Elmer config file),
    * creates spectral analysis of the results as pdf images with peaks 
      that are correctly labeled.
"""

"""
IMPORTS
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import NullFormatter

from scipy import signal
import pandas as pd
from math import ceil
import argparse
import glob
import sys
import os
import fnmatch
import re
from math import sqrt

"""
CONFIGURATION
"""

plt.rc('font', family='Arial')

interesting_quantities = ['displacement 1','displacement 2', 'pressure']

labels = pd.DataFrame({'quantity' : interesting_quantities, 
                    'labels' : ['x','y','p'], 
                    'units': ['m', 'm', 'Pa'],
                    'factors': ['1.0', '1.0', '1.0'] })

parameters = pd.DataFrame({'parameter' : ['vmax','hdist', 'ymfold', 'ymepithelium'], 
                    'labels' : ['v_\mathrm{max}','h_\mathrm{dist}', 'E_\mathrm{m}', 'E_\mathrm{ep}'], 
                    'units': ['m\cdot s^{-1}', 'cm','Pa','Pa'],
                    'title': ['maximální rychlosti', 'vzdálenosti hlasivek', 'Youngova modulu svalu', 'Youngova modulu epitelu']      })

"""
FUNCTIONS BLOCK
"""

def plot_quantity(title, labely, time, quantity, figno, factor, fig, figform,sharex=False,sharey=False):
    """ Plots a graph of a quantity as a function of time. """
    
    ax = fig.add_subplot(figform[0],figform[1],figno)
    
    
        
    # correct formating of the y axis (in milimeters)
    #ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: ('%.2f')%(x*factor)))
    plt.xlim(min(time),max(time))
    ax.plot(time, quantity)

    if title: 
        ax.text(.5,.85,title,
        horizontalalignment='center',
        transform=ax.transAxes)

    # sharing axes
    if sharey and figno % figform[1] == 0:
        ax.yaxis.set_major_formatter( NullFormatter() )
    else:
        plt.ylabel(labely)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    if (sharex and figno != figform[0]*figform[1] and figno != figform[0]*figform[1] - 1): 
        ax.xaxis.set_major_formatter( NullFormatter() )
    else:
        plt.xlabel('$t$ [s]')
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))


    
    return 0

def plot_fs_quantity(title, labely, time, quantity, figno, fig, figform,freqcut=300):
    """ Plot a graph of a spectral density of given quantity as a function of frequency. """
    
    bx = fig.add_subplot(figform[0],figform[1],figno)

    dt = time[1]-time[0]

    # by default includes only positive frequencies, that is
    # due to Nyquist frequency returns only max fs/2

    if min(quantity)==max(quantity): return 0

    plt.yscale('log')
    plt.ylabel(labely)
    if title: plt.title(title)
    print(str(title))
    plt.xlabel('$f$ [Hz]')

    # sampling frequency:
    fs=1.0/dt
    period=max(time)-min(time)
    f, Pxx_den = signal.periodogram(quantity, fs)
    
    # find peaks
    indexes = peakutils.indexes(Pxx_den, thres=0.001, min_dist=5) # find peaks
    maxind = np.argmax(Pxx_den)
    
    peak=[f[maxind],Pxx_den[maxind]]
    peaks=[f[indexes],Pxx_den[indexes]]

    # show frequencies either cut or some basic ones 
    myxmax = max(freqcut, 5.0/period) 
    plt.xlim(min(f),myxmax)
    plt.ylim([1.05*max(Pxx_den)/1000,max(Pxx_den)])

    line = plt.plot(f, Pxx_den) 
    
    print('Maximum peak:')
    print(peak[0])
    bx.annotate(
        '$f_\mathrm{max}=%.2f \mathrm{\,Hz}$' % float(peak[0]), xy=peak, xycoords='data',
        xytext=(10, 5), textcoords='offset points',
        horizontalalignment='left', verticalalignment='bottom')
    
    # period shift - draw spectrum of second half of motion
    if len(f)<1000: 
        print('Too short time to draw time shifted freq analysis')
        return 0
    
    ind=ceil(np.argmax(time)/2.0)
    f2, Pxx_den2 = signal.periodogram(quantity[ind:], fs)
    line2 = plt.plot(f2, Pxx_den2) 
    
    indexes2 = peakutils.indexes(Pxx_den2, thres=0.001, min_dist=5) # find peaks
    maxind2 = np.argmax(Pxx_den2)
    peak2=[f2[maxind2],Pxx_den2[maxind2]]

    bx.annotate(
        '$f\'_\mathrm{max}=%.2f \mathrm{\,Hz}$' % float(peak2[0]), xy=peak2, xycoords='data',
        xytext=(20, -10), textcoords='offset points',
        horizontalalignment='left', verticalalignment='bottom')    
    
    print(peaks)


    return peak    

def myspacing(mg=0.1,ps=0.7):
    axspace=0.07
    plt.subplots_adjust(left=mg+axspace, bottom=mg+axspace, right=1-mg, top=1-mg, wspace=ps, hspace=ps+axspace)
    return 0

def ytable(bn = 2):
    """ Return the table with y-coordinates of the given boundary. """

    allboundaries = pd.read_table ( 'mesh/mesh.boundary',header=None, 
                                    sep=' ', names=['bn', 'pn'], 
                                    usecols = (1, 5), 
                                    dtype={'bn':np.int32,'pn':np.int32}, 
                                    index_col='pn')
    myboundaries = allboundaries[ allboundaries.bn == int(bn) ] 
    allpoints = pd.read_table ('mesh/mesh.nodes',header=None, sep=' ', names=['pn', 'y'], usecols = (0, 3), index_col='pn' )
    mycoords = pd.merge(myboundaries, allpoints, how='inner', left_index=True, right_index=True )
    return mycoords

def standard_probes():
    """ Returns the position of points of probes defined on the standard geometry. """
    probesdf = pd.DataFrame()
    
    # calculate position of the top of the lower vocal fold
    mycoords = ytable(bn=2)
    probesdf = probesdf.append({'pn':str(mycoords['y'].idxmax()), 
                                'label':'1',
                                'name':'spodní hlasivka'}, ignore_index=True)
    
    # calculate position of the bottom of the upper vocal fold
    mycoords = ytable(bn=19)
    probesdf = probesdf.append({'pn':str(mycoords['y'].idxmin()), 
                                'label':'2',
                                'name':'horní hlasivka'}, ignore_index=True)

    # calculate the middle of the outlet
    mycoords = ytable(bn=26)
    avg=(mycoords['y'].max()+mycoords['y'].min())/2.0
    mycoords['dist'] = abs(avg-mycoords['y'])
    probesdf = probesdf.append({'pn':str(mycoords['dist'].idxmin()), 
                                'label':'out',
                                'name':'výtok'}, ignore_index=True)

    # calculate the middle of the inlet
    mycoords = ytable(bn=25)
    avg=(mycoords['y'].max()+mycoords['y'].min())/2.0
    mycoords['dist'] = abs(avg-mycoords['y'])

    probesdf = probesdf.append({'pn':str(mycoords['dist'].idxmin()), 
                                'label':'in',
                                'name':'vtok'}, ignore_index=True)
    
    return probesdf

def print_standard_probes():
    """ Returns the position of points of probes defined on the standard geometry. """
    
    probes = standard_probes()
    print(' '.join(map(str, probes['pn'].values)))

def read_sensor_names():
    """ Return the table of sensor names. """
    nametable = pd.read_table ( 'Transient/sensors.dat.names',skiprows=4, 
                                names=['column', 'quantity', 'pn'], 
                                usecols = (0, 2, 3), skipinitialspace=True,
                                sep='\s*at node \s*|\s*:\s*', 
                                engine='python')
    return nametable

def this_sensor_table(sensor_id,nametable=None):
    if nametable is None: nametable = read_sensor_names()
    mytable = nametable[ nametable.pn == int(sensor_id) ]
    return mytable

def graphs_for_probe(proberow, sensorsdata):
    # filter by those that we find interesting_quantities
    mytable=this_sensor_table(proberow['pn'])
    tableofgraphs = pd.merge(labels, mytable, how='inner', on='quantity')

    # we shall now typeset the graphs for all the quantities and points
    fig = plt.figure(figsize=(6, 2*len(tableofgraphs.index)), dpi=250)
    fig.suptitle = str( proberow['name'])+' ('+str(proberow['label'])+')'
    figform = [len(tableofgraphs.index), 2] # [ vert, hor ]
    figno = 0
    time = sensorsdata[:,0]
    
    for index, quantityrow in tableofgraphs.iterrows():
        quantity = sensorsdata[:,quantityrow['column']-1]
    #    title = ('$'+str(quantityrow['labels'])+
    #            '_{'+str(proberow['label'])+'}$ ')
        labely = ('$'+str(quantityrow['labels'])+
                 '_{\mathrm{'+str(proberow['label'])+
                 '}}\,\mathsf{['+str(quantityrow['units'])+']}$' )
        labelfy = ('spektrum $'+str(quantityrow['labels'])+
                  '_{\mathrm{'+str(proberow['label'])+
                  '}}\,\mathsf{{['+str(quantityrow['units'])+'}^2/Hz]}$' )
        figno += 1
        plot_quantity('', labely, time, quantity, 
                     figno, float(quantityrow['factors']), fig, figform)

        figno += 1
        plot_fs_quantity('', labelfy, time, quantity,
                      figno, fig, figform)
    plt.tight_layout()
    plt.savefig(str(proberow['label'])+'.pdf',format='pdf')
    plt.close()

def generate_graphs(cut=True):
    sensorsdata = np.genfromtxt('Transient/sensors.dat')

    # find the moment of interaction and cut the data
    if cut:
        for i in range(len(sensorsdata[:,1])):
            if sensorsdata[i,1] != 0.00: break
        sensorsdata=sensorsdata[(i-1):,:]
    
    if len(sensorsdata)<=2: 
        print("Not enough points to generate graph")
        return 0
    # for each probe we shall generate the graphs of the interesting_quantities
    probesdf = standard_probes()

    # print(probesdf)

    for index, proberow in probesdf.iterrows():
        graphs_for_probe(proberow, sensorsdata)
    return 0

def cut_zeros(sensorsdata):
    for i in range(len(sensorsdata[:,1])):
        if sensorsdata[i,1] != 0.00: break
    sensorsdata=sensorsdata[(i-1):,[0,2]] # select time and dispy
    return sensorsdata

def generate_oneplot(cut=True):
    sensorsdata = np.genfromtxt('Transient/sensors.dat')

    # find the moment of interaction and cut the data
    
    sensorsdata = cut_zeros(sensorsdata)
    
    np.savetxt("mysensor.csv", sensorsdata, delimiter=",")

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def generate_comparison():
    

    path = '.'

    configfiles = [dirpath
    
    for dirpath, dirnames, files in os.walk(path, followlinks=True)
    for f in fnmatch.filter(files, 'config.ini')]


    configfiles.sort(key=natural_keys)

    fig = plt.figure(figsize=(6, 8), dpi=250)        
    figform = [ceil(len(configfiles)/2),2]
    figno = 0
    
    for mydir in configfiles:
        myfile = str(mydir)+'/Transient/sensors.dat'
        figno += 1
        sensorsdata = np.genfromtxt(myfile)
        
        time = sensorsdata[:,0]
        ycoords = sensorsdata[:,1]
        
        for j in range(len(time)):
            if time[j] >= 0.05: break
        
        time = time[:j]
        ycoords = ycoords[:j]
        
        plotname = re.sub(r'[./]', '', mydir)
        plot_quantity(plotname, '$ y_1 \mathrm{\, [m]} $', time, ycoords, figno, 1e3, fig, figform, sharex=True,sharey=True)
        
        ax = plt.gca()
        
        plt.ylim(-1.7e-4,0.4e-4)
        plt.locator_params(nbins=6,axis='y', tight=True)
        plt.locator_params(nbins=5,axis='x', tight=True)
        plt.grid(which='major', axis='y')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')


    
    #plt.tight_layout()
    myspacing(mg=0.04,ps=0.2)
    plt.savefig('comparison.pdf',format='pdf')
    plt.close()

def read_config_float(configfile, floatname):
    """ Read float value with key floatname from configfile in ini format
    """
    
    try:
        f = open(configfile)
    except IOError:
        print("Could not open the file "+configfile)
    
    myline=None
    value=None
    for line in f:
        fields = line.strip().split('=')
        if fields[0]==floatname: 
            myline = fields[1]
            break
    if myline:
        value = myline.split('#')
        value = float(value[0])
    if value: 
        return value
    else:
        return 0

def equals(one, two, eps=1.0e-4):
    """ Are the argument floats equal? (within the rel. tolerance)
    """
    dif=abs(one-two)
    rel=2.0*dif/(abs(one)+abs(two))
    if rel<eps: return True
    else: return False


def parametric_study(parameter):
    
    # find all files config.ini in subdirectories
    
    # assume we are in the config.ini directory

    import peakutils
    import math
    
    path = '.'
    configfiles = [dirpath
    
    for dirpath, dirnames, files in os.walk(path, followlinks=True)
    for f in fnmatch.filter(files, 'config.ini')]
    
    parameter_table = pd.DataFrame( columns=['parameter', 'frequency', 'spectrum', 'convergence', 'source' ] )
    
    i = 0    
    for mydir in configfiles:
        configfile = mydir+'/config.ini'       
        value = read_config_float(configfile, parameter)
        if not value: return 0
        
        sensorsdatafile = mydir+'/Transient/sensors.dat'
        try:
            sensorsdata = np.genfromtxt(sensorsdatafile)
        except IOError: 
            print("Cannot read the file "+sensorsdatafile)
            continue
        
        time = sensorsdata[:,0]
        quantity = sensorsdata[:,1]
        
        # check for convergence of simulation
        print('Checking for convergence')

        if equals(config_time(configfile),max(time)):
            convergence = True
        else:
            convergence = False
        print ('file '+mydir+' has convergence '+str(convergence))
        
        sensorsdata = cut_zeros(sensorsdata)

        dt = time[1]-time[0]
        fs = 1.0/dt
        f, Pxx_den = signal.periodogram(quantity, fs)
        
        # cut frequencies bellow 5 Hz
        for j in range(len(f)):
            if f[j] > 5.0: break
        f = f[j:]
        Pxx_den = Pxx_den[j:]
        
        # find peaks
        indexes = peakutils.indexes(Pxx_den, thres=0.001, min_dist=5) # find peaks
        
        i += 1
        this_frame = pd.DataFrame({
                        'parameter': value*np.ones(len(indexes)),
                        'frequency': f[indexes], 
                        'spectrum': Pxx_den[indexes],
                        'convergence': convergence,
                        'source': 'fsi' })
        parameter_table = pd.concat( [parameter_table, this_frame], ignore_index=True )
        #pd.options.display.max_rows = 999
        
        # add the data from modal analysis
        thisymfold = read_config_float(configfile, 'ymfold')
        thisymepithelium = read_config_float(configfile, 'ymepithelium')
        
        templatedir = '/home/jakub/diplomka/code/16-Automated-Transient/template/'
        defaultconfig = templatedir+'config.ini' 
        defaultymfold = read_config_float(defaultconfig, 'ymfold')
        defaultymepithelium = read_config_float(defaultconfig, 'ymepithelium')
        
        sameymfold = ( not thisymfold ) or equals(thisymfold,defaultymfold)
        sameymepithelium = ( not thisymepithelium ) or equals(thisymepithelium,defaultymepithelium)
        
        if sameymfold and sameymepithelium:
            modalsource=templatedir+'Eigenvalues.dat'
        else:
            modalsource=mydir+'/Modal/Eigenvalues.dat'

        try:
            modaldata = np.genfromtxt(modalsource)
        except IOError: 
            print("Cannot read the file "+modalsource)
            continue        

        this_frame = pd.DataFrame({
                        'parameter': value*np.ones(len(modaldata)),
                        'frequency': modaldata, 
                        'source': 'modal' })
        parameter_table = pd.concat( [parameter_table, this_frame], ignore_index=True )        
    
    return(parameter_table)

def graph_parametric_study(parameter):
    
    parameter_table = parametric_study(parameter)
    
    fig, ax = plt.subplots(1,1)

    unit = parameters[ parameters.parameter == parameter ].to_string(columns=['units'], header=False, index=False)
    label = parameters[ parameters.parameter == parameter ].to_string(columns=['labels'], header=False, index=False)
    title = parameters[ parameters.parameter == parameter ].to_string(columns=['title'], header=False, index=False)

    plt.title('Vliv '+title+' $'+label+'$ na spektrum')
    plt.ylabel('$'+label+'\,\mathrm{['+unit+']}$')
    plt.xlabel('$f\,\mathrm{[Hz]}$')
    plt.xlim(0,200)

    # select decent y limiters
    unique_parameters=np.unique(parameter_table['parameter'])
    mystep=min(abs(np.diff(unique_parameters)))
    ymin=0
    if min(unique_parameters)>3*mystep: ymin=min(unique_parameters)-mystep
    plt.ylim(ymin,max(unique_parameters)+mystep)
    

    for parameter_value in unique_parameters:
        this_parameter_table = parameter_table[ (parameter_table.parameter == parameter_value) & (parameter_table.source == 'fsi') ].copy()
        normalization_factor = max(this_parameter_table['spectrum'])
        this_parameter_table['spectrum'] *= 1/normalization_factor
        this_parameter_table['spectrum'] = this_parameter_table['spectrum'].map(lambda x: sqrt(sqrt(x)))
        
        if all(this_parameter_table['convergence']):
            color = 'b'
        else: 
            color = 'r'
           
        mycolors=this_parameter_table['spectrum'].map(lambda x: colors.colorConverter.to_rgba(color, float(x)) )
        
        ax.scatter(this_parameter_table['frequency'], this_parameter_table['parameter'], s=200*this_parameter_table['spectrum'], color=mycolors, marker='+', linewidths=4)
        
        modal_parameter_table = parameter_table[ (parameter_table.parameter == parameter_value) & (parameter_table.source == 'modal') ].copy()
        ax.scatter(modal_parameter_table['frequency'], modal_parameter_table['parameter'], color='g', marker='|', linewidths=3, s=200.0*np.ones(len(modal_parameter_table['frequency'])))

        
        print(this_parameter_table)
        print(modal_parameter_table)

    plt.tight_layout()
    plt.savefig(str(parameter)+'.pdf',format='pdf')
    plt.close()

def config_time(configfile):
    """Returns the config time of simulation it was supposed to run."""
    
    step = read_config_float(configfile, 'step')
    intervals = read_config_float(configfile, 'intervals')
    T_config = step*intervals
    
    return T_config
        
"""
MAIN PROGRAM
"""

parser = argparse.ArgumentParser()
parser.add_argument("--points", action='store_true',
                    help="show the IDs of the standard points")
parser.add_argument("--graphs", action='store_true',
                    help="produce graphs for the given mesh and data")
parser.add_argument("--nocut", action='store_true',
                    help="do not cut time interval")
parser.add_argument("--oneplot", action='store_true',
                    help="produce simple csv file for the lower fold")
parser.add_argument("--compare", action='store_true',
                    help="compare the csv y-coord")
parser.add_argument("-ps", "--parameter", type=str,
                    help="parametric study on subdirectory")
args = parser.parse_args()

if args.points: 
    print_standard_probes()
if args.graphs:
    import peakutils
    if args.nocut:
        generate_graphs(False)
    else:
        generate_graphs()   
if args.oneplot:
    generate_oneplot()     
if args.compare:
    generate_comparison()  
if args.parameter:
    graph_parametric_study(args.parameter)
    
