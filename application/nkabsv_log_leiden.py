#coding: utf-8
import numpy as np
import numpy
import math
import cmath
from os import system
import os
import glob
from flask import Flask, flash

def kramers_kronig(d1, n0, n2, mp):
   """Convert Celsius to Fahrenheit degrees."""
   if d1:
     thickness = float(d1) * 1e-4
     d = thickness
     nvis = float(n0)
     no=nvis
     nsubs = float(n2)
     n2=nsubs
     mape = float(mp)
     Error = mape/100.
     
     DIR = os.getcwd() + '/'

     inp_file = glob.glob(DIR + 'application/uploads/*.txt')
     filename = np.loadtxt(inp_file[0])
     #print('Shape is:', filename.shape)
     i = filename.shape[0]
     with open(inp_file[0], 'r') as f2:
       lines = f2.readlines()

     data = []
     data = [line.split() for line in lines]
     data2 = np.asfarray(data)
     xAb = data2[:,0]
     yAb = data2[:,1]

     #############################################################################
     # 1. CONVERT AB to Texp 
     #############################################################################
     #print(DIR)
     
     f = open(DIR+'application/uploads/T_EXP.txt', 'w')
     for i1 in range(i):
       Tx = 1./(10**yAb[i1])
       f.write('{0:f} {1:f} \n'.format(xAb[i1], Tx))
     f.close()

     #############################################################################
     # 2. Calculate the value of k(imag)
     #############################################################################
     f = open(DIR+'application/uploads/COEF.txt', 'w')
     for i2 in range(i):
       init = 1.
       f.write('{0:f} {1:f}\n'.format(xAb[i2], init))
     f.close()

     NI = 0
     result = 1.
     while result > Error:
       with open(DIR+'application/uploads/COEF.txt', 'r') as f3:
         lines3 = f3.readlines()
       dataC = []
       dataC = [line3.split() for line3 in lines3]
       data3 = np.asfarray(dataC)
       xC = data3[:,0]
       yt01 = data3[:,1]
       
       f = open(DIR+'application/uploads/K.txt', 'w')
       for i3 in range(i):
         alpha = (1./d)*(2.3*yAb[i3] + 2.*(np.log(yt01[i3])))
         imag = alpha/(12.5*xC[i3])
         f.write('{0:f} {1:f} \n'.format(xC[i3], imag))
       f.close()

       with open(DIR+'application/uploads/K.txt', 'r') as f4:
         lines4 = f4.readlines()
       
       datak = []
       datak = [line4.split() for line4 in lines4]
       data4 = np.asfarray(datak)
       xk = data4[:,0]
       yk = data4[:,1]

       f = open(DIR+'application/uploads/N.txt', 'w')
       for g in range(i):
         h = (xk[i-1] - xk[i-i])/i
         fodd = 0
         feven = 0
         if g % 2 != 0:
           j = i
           for g1 in range(j):
             if g1 % 2 == 0:
               foddsum = fodd + 0.5*(((yk[g1])/(xk[g1]-xk[g]))+((yk[g1])/(xk[g1]+xk[g])))
               fodd = foddsum
         else:
           j1 = i
           for g2 in range(j1):
             if g2 % 2 != 0:
               fevensum = feven + 0.5*(((yk[g2])/(xk[g2]-xk[g]))+((yk[g2])/(xk[g2]+xk[g])))
               feven = fevensum
          
         soma = fodd + feven
         np1 = (2./3.14)*(2.*h)*soma
         VAL = (NI + 1)
         real = no + np1
         Porc = ((g+1.)/i)*100.
         f.write('{0:f} {1:f} \n'.format(xk[g], real))
       f.close()

       with open(DIR+'application/uploads/N.txt', 'r') as f5:
         lines5 = f5.readlines()
       
       datan = []
       datan = [line5.split() for line5 in lines5]
       data5 = np.asfarray(datan)
       xn = data5[:,0]
       yn = data5[:,1]

       f = open(DIR+'application/uploads/T_TEO.txt', 'w')
       for v in range(i):
         n = complex(yn[v],yk[v])
         t01 = 2*no/(no + n)
         t12 = 2*n/(n+n2)
         t02 = 2*no/(no+n2)
         r01 = (no - n)/(no + n)
         r12 = (n - n2)/(n + n2)
         Ex1 = math.exp(-12.5*d*xk[v]*yk[v])
         Ex2 = cmath.exp(2j*(6.28*xk[v]*d*n))
         Trans = Ex1*((abs((t01*t12/t02)/(1. + r01*r12*Ex2)))**2)
         f.write('{0:f} {1:f} \n'.format(xk[v], Trans))
       f.close()

       f = open(DIR+'application/uploads/COEF.txt', 'w')
       for vv in range(i):
         n = complex(yn[vv],yk[vv])
         t01 = 2*no/(no + n)
         t12 = 2*n/(n+n2)
         t02 = 2*no/(no+n2)
         r01 = (no - n)/(no + n)
         r12 = (n - n2)/(n + n2)
         Ex2 = cmath.exp(2j*(6.28*xk[vv]*d*n))
         fator = abs((t01*t12/t02)/(1. + r01*r12*Ex2))
         f.write('{0:f} {1:f}\n'.format(xk[vv], fator))
       f.close()

       with open(DIR+'application/uploads/T_TEO.txt', 'r') as f6:
         lines6 = f6.readlines()
       
       dataTt = []
       dataTt = [line6.split() for line6 in lines6]
       data6 = np.asfarray(dataTt)
       xTt = data6[:,0]
       yTt = data6[:,1]

       with open(DIR+'application/uploads/T_EXP.txt', 'r') as f7:
         lines7 = f7.readlines()

       dataTe = []
       dataTe = [line7.split() for line7 in lines7]
       data7 = np.asfarray(dataTe)

       xTe = data7[:,0]
       yTe = data7[:,1]

       mapee = []
       for rr in range(i):
         mapee.append(math.fabs((1./i)*(yTe[rr] - yTt[rr])/yTt[rr]))
       result = np.sum(mapee)

       chi = []
       for rr1 in range(i):
         chi.append(((yTe[rr1] - yTt[rr1])**2)/yTt[rr1])
       result1 = np.sum(chi)	
      
       NI = NI + 1
     import shutil
     from shutil import make_archive
     shutil.make_archive('outputs_optc_const', 'zip','/Users/willrocha/T0/ice-database/application/uploads')
     flash('Calculation is done!', 'success')
     return thickness,nvis,nsubs,Error
   else:
     print('No entry!')
     pass

