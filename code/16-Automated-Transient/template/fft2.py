# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy import signal
import peakutils
from peakutils.plot import plot as pplot

# reading from csv
colnames = ['time', 'pressure', 'x','y']
csv = np.genfromtxt ('data.csv', delimiter=",",skip_header=1)

time = csv[:,0]
dispx = csv[:,2]

# fourier transform

f, Pxx_den = signal.periodogram(dispx, fs=1.0/0.0001)
indexes = peakutils.indexes(Pxx_den, thres=0.5, min_dist=30) # find peaks
peak=(f[indexes[0]],Pxx_den[indexes[0]])
print(peak) # print frequency peaks

# plotting
fig = plt.figure()
#plt.tight_layout() # more space between plots

ax = fig.add_subplot(211)
plt.xlabel('čas $t$ [s]')
plt.ylabel('$x_\mathrm{A}$ [mm]')
plt.title('Pohyb hlasivky v závislosti na čase')
# correct formating of the y axis (in milimeters)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: ('%.2f')%(x*1e3)))
ax.plot(time, dispx)

bx = fig.add_subplot(212)
plt.xlim([5,500])
plt.ylim([1e-15,1e-9])
line = plt.plot(f, Pxx_den) # plot from peakutils to mark the peak
plt.yscale('log')
#plt.setp(line,linestyle='solid')
plt.xlabel('frekvence $f$ [Hz]')
plt.ylabel('spektrální hustota $ [\mathrm{m^2/Hz}]$')
plt.title('Spektrum pohybu hlasivky')

bx.annotate('$f_\mathrm{max}=%.2f \mathrm{\,Hz}$' % peak[0], xy=peak, xycoords='data',
                xytext=(0, 20), textcoords='offset points',
                arrowprops=dict(arrowstyle='->'),
                horizontalalignment='center', verticalalignment='bottom',
                )

#bx.annotate('maximum $f_\mathrm{max}='+Pxx_den[indexes[0]]+'\,\mathrm{Hz}$', xy=(f[indexes[0]],Pxx_den[indexes[0]],), arrowprops=dict(facecolor='black', shrink=0.05))

#adjust spacing
mg=0.1
ps=0.7
plt.subplots_adjust(left=mg, bottom=mg, right=1-mg, top=1-mg, wspace=ps, hspace=ps)

plt.show()

"""
plt.semilogy(f, Pxx_den)
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.show()

#print(*xt, sep="\n")

fig, (ax, bx) = plt.subplots()

ax.plot(t, 2.0/N * x[:N/2])
bx.plot(omf, 2.0/N * np.abs(xf[:N/2]))
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.show()
"""
