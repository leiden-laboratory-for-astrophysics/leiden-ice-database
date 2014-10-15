#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  csv_to_h5.py
#  
#  2014 Bart Olsthoorn <olsthoorn@vlij.strw.leidenuniv.nl>
#  

import sys

import numpy as np
import h5py
import time
import matplotlib.pyplot as plt

# Convert CSV to HPF5
t = time.time()

f = h5py.File('ice.h5', 'w')

data = np.genfromtxt(sys.argv[1])

dset = f.create_dataset('mydataset', data.shape, dtype='float64')
dset[...] = data
dset.attrs['temperature'] = 15

print "Converted to HPF5 in ", time.time()-t, "seconds"

# Plot data with matplotlib
t = time.time()

x = data[:,0]
y = data[:,1]

print "Maximum absorbance ", y[y.argmax()], " at ", x[y.argmax()], " cm-1"

fig = plt.figure()

ax1 = fig.add_subplot(111)
ax1.plot(x, y)
ax2 = ax1.twiny()

ax1.set_xlabel(r'Wavenumber $\rm cm^{-1}$')

ax2.set_xlabel(r'$\lambda$ $\mu m$')
ax2_locations = np.array([3333, 2000, 1000, 500])

def tick_function(X):
    V = 10000.0/X
    return ["%d" % z for z in V]

ax2.set_xticks(ax2_locations)
ax2.set_xticklabels(tick_function(ax2_locations))


ax1.set_xlim(500, 4000)
ax2.set_xlim(500, 4000)

ax1.invert_xaxis()
ax2.invert_xaxis()

plt.ylim(-0.01, 0.30)
ax1.set_ylabel(r'Absorbance')
plt.text(0.5, 1.12, sys.argv[1], #r'Pure $\rm H_{2}O$ at 15 K',
    horizontalalignment='center',
    fontsize=14,
    transform = ax2.transAxes)

plt.tight_layout(pad=4.0)
plt.savefig('plot.eps', bbox_inches='tight')

# for x, y in row:
#    print "%f, %f" % (x, y)

