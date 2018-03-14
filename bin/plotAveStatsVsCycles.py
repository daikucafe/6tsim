#!/usr/bin/python
"""
\brief Plots statistics with a selected parameter.

\author Thomas Watteyne <watteyne@eecs.berkeley.edu>
\author Kazushi Muraoka <k-muraoka@eecs.berkeley.edu>
\author Nicola Accettura <nicola.accettura@eecs.berkeley.edu>
\author Xavier Vilajosana <xvilajosana@eecs.berkeley.edu>
"""

#============================ adjust path =====================================

#============================ logging =========================================

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('plotStatsVsParameter')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ imports =========================================

import os
import re
import glob
import sys
import math

import numpy
import scipy
import scipy.stats

import logging.config
import matplotlib.pyplot as plt
import argparse
import random

#============================ defines =========================================

CONFINT = 0.95

COLORS = [
   '#0000ff', #'b'
   '#ff0000', #'r'
   '#008000', #'g'
   '#bf00bf', #'m'
   '#000000', #'k'
   '#ff0000', #'r'

]

LINESTYLE = [
    '--',
    '-.',
    ':',
    '-',
    '-',
    '-',
]

ECOLORS= [
   '#0000ff', #'b'
   '#ff0000', #'r'
   '#008000', #'g'
   '#bf00bf', #'m'
   '#000000', #'k'
   '#ff0000', #'r'
]

#============================ body ============================================

def parseCliOptions():

    parser = argparse.ArgumentParser()

    parser.add_argument( '--statsName',
        dest       = 'statsName',
        nargs      = '+',
        type       = str,
        default    = 'numTxCells',
        help       = 'Name of the statistics to be used as y axis.',
    )

    options        = parser.parse_args()

    return options.__dict__

#===== statistics vs cycle

def plot_statsVsCycle(statsName):

    dataDirs = []
    for dataDir in os.listdir(os.path.curdir):
        if os.path.isdir(dataDir):
            if (statsName == 'probableCollisions' or statsName == 'effectiveCollidedTxs') and dataDir=='no interference':
                continue
            dataDirs += [dataDir]

    stats      = {}

    # One curve is generated by each dataDir
    for dataDir in dataDirs:

        # assume that each dataDir has one directory which includes multiple file
        statsPerDir = {}

        for infilename in glob.glob(os.path.join(dataDir,'*.dat')):

            # find numCyclesPerRun
            with open(infilename,'r') as f:
                for line in f:

                    if line.startswith('##'):

                        # numCyclesPerRun
                        m = re.search('numCyclesPerRun\s+=\s+([\.0-9]+)',line)
                        if m:
                            numCyclesPerRun    = int(m.group(1))

            # find colnumcycle
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('# '):
                        elems                   = re.sub(' +',' ',line[2:]).split()
                        numcols                 = len(elems)
                        colnumstatsName         = elems.index(statsName)
                        colnumcycle             = elems.index('cycle')
                        colnumrunNum            = elems.index('runNum')
                        break

            # parse data
            previousCycle  = None
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    m = re.search('\s+'.join(['([\.0-9]+)']*numcols),line.strip())
                    stat                = int(m.group(colnumstatsName+1))
                    cycle               = int(m.group(colnumcycle+1))
                    runNum              = int(m.group(colnumrunNum+1))

                    if cycle not in statsPerDir:
                        statsPerDir[cycle] = []
                    statsPerDir[cycle] += [stat]

                    if cycle==0 and previousCycle and previousCycle!=numCyclesPerRun-1:
                        print 'runNum({0}) in {1} is incomplete data'.format(runNum-1,dir)

                    previousCycle = cycle

            stats[dataDir] = statsPerDir

    xlabel         = 'slotframe cycles'

    if statsName == 'numTxCells':
        ylabel = 'Tx cells'
    elif statsName == 'scheduleCollisions':
        ylabel = 'schedule collisions'
    elif statsName == 'droppedAppFailedEnqueue':
        ylabel = 'dropped packets due to full queue'
    elif statsName == 'effectiveCollidedTxs':
        ylabel = 'potentially colliding transmitters'
    elif statsName == 'probableCollisions':
        ylabel = 'probable collisions'
    else:
        ylabel = statsName

    outfilename    = 'output_{}_cycle'.format(statsName)

    # plot figure for
    genStatsVsCyclePlots(
        stats,
        dirs           = dataDirs,
        outfilename    = outfilename,
        xlabel         = xlabel,
        ylabel         = ylabel,
    )

#===== dropped packets vs cycle

def plot_droppedDataPacketsVsCycle():

    dataDirs = []
    for dataDir in os.listdir(os.path.curdir):
        if os.path.isdir(dataDir):
            dataDirs += [dataDir]

    stats      = {}

    # One curve is generated by each dataDir
    for dataDir in dataDirs:

        # assume that each dataDir has one directory which includes multiple files
        statsPerDir = {}
        for infilename in glob.glob(os.path.join(dataDir,'*.dat')):

            # find numCyclesPerRun
            with open(infilename,'r') as f:
                for line in f:

                    if line.startswith('##'):

                        # numCyclesPerRun
                        m = re.search('numCyclesPerRun\s+=\s+([\.0-9]+)',line)
                        if m:
                            numCyclesPerRun    = int(m.group(1))

            # find colnumcycle
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('# '):
                        elems                         = re.sub(' +',' ',line[2:]).split()
                        numcols                       = len(elems)
                        colnumdroppedAppFailedEnqueue = elems.index('droppedDataFailedEnqueue')
                        colnumdroppedMacRetries       = elems.index('droppedDataMacRetries')
                        colnumcycle                   = elems.index('cycle')
                        colnumrunNum                  = elems.index('runNum')
                        break

            # parse data
            previousCycle  = None
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    m = re.search('\s+'.join(['([\.0-9]+)']*numcols),line.strip())
                    droppedAppFailedEnqueue = int(m.group(colnumdroppedAppFailedEnqueue+1))
                    droppedMacRetries       = int(m.group(colnumdroppedMacRetries+1))
                    cycle                   = int(m.group(colnumcycle+1))
                    runNum                  = int(m.group(colnumrunNum+1))

                    if cycle not in statsPerDir:
                        statsPerDir[cycle] = []
                    statsPerDir[cycle] += [droppedAppFailedEnqueue+droppedMacRetries]

                    if cycle==0 and previousCycle and previousCycle!=numCyclesPerRun-1:
                        print 'runNum({0}) in {1} is incomplete data'.format(runNum-1,dir)

                    previousCycle = cycle

            stats[dataDir] = statsPerDir

    xlabel = 'slotframe cycles'
    ylabel = 'dropped packets'
    outfilename    = 'output_dropped_cycle'

    # plot figure for
    genStatsVsCyclePlots(
        stats,
        dirs           = dataDirs,
        outfilename    = outfilename,
        xlabel         = xlabel,
        ylabel         = ylabel,
        ymin           = -0.000001
    )

#============================ plotters ========================================

def genStatsVsCyclePlots(vals, dirs, outfilename, xlabel, ylabel, xmin=False, xmax=False, ymin=False, ymax=False, log = False):

    # print
    print 'Generating {0}...'.format(outfilename),

    plt.figure()
    plt.xlabel(xlabel, fontsize='large')
    plt.ylabel(ylabel, fontsize='large')
    if log:
        plt.yscale('log')

    for dataDir in dirs:
        # calculate mean and confidence interval
        meanPerParameter    = {}
        confintPerParameter = {}
        for (k,v) in vals[dataDir].items():
            a                        = 1.0*numpy.array(v)
            n                        = len(a)
            se                       = scipy.stats.sem(a)
            m                        = numpy.mean(a)
            confint                  = se * scipy.stats.t._ppf((1+CONFINT)/2., n-1)
            meanPerParameter[k]      = m
            confintPerParameter[k]   = confint

        # plot
        x         = sorted(meanPerParameter.keys())
        y         = [meanPerParameter[k] for k in x]
        yerr      = [confintPerParameter[k] for k in x]

        if dataDir == 'tx-housekeeping':
            index = 0
        elif dataDir == 'rx-housekeeping':
            index = 1
        elif dataDir == 'tx-rx-housekeeping':
            index = 2
        elif dataDir == 'no housekeeping':
            index = 3
        elif dataDir == 'no interference':
            index = 4
        else:
            index = random.randint(0,4)

        plt.errorbar(
            x        = x,
            y        = y,
            #yerr     = yerr,
            color    = COLORS[index],
            ls       = LINESTYLE[index],
            ecolor   = ECOLORS[index],
            label    = dataDir
        )

        datafile=open(outfilename+'.dat', "a")
        print >> datafile,dataDir
        print >> datafile,xlabel,x
        print >> datafile,ylabel,y
        #print >> datafile,'conf. inverval',yerr

    plt.legend(prop={'size':12},loc=0)
    if xmin:
        plt.xlim(xmin=xmin)
    if xmax:
        plt.xlim(xmax=xmax)
    if ymin:
        plt.ylim(ymin=ymin)
    if ymax:
        plt.ylim(ymax=ymax)

    plt.savefig(outfilename + '.png')
    plt.savefig(outfilename + '.eps')
    plt.close('all')

    # print
    print 'done.'

#============================ main ============================================
def main():

    # parse CLI option
    options      = parseCliOptions()
    statsName    = options['statsName']

    for statsName in options['statsName']:
        # stats vs cycle
        plot_statsVsCycle(statsName)

    # plot dropped packets vs cycle
    plot_droppedDataPacketsVsCycle()

if __name__=="__main__":
    main()
