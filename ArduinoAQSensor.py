# -*- coding: utf-8 -*-

“””

Code to be used with an Arduino and Plantower sensor to measure air quality

Arduino must have proper read code installed

Written by Anthony (Tony) Butterfield, Department of Chemical Engineering

University of Utah

“””

import serial #Import Serial Library

import numpy as np

import matplotlib.pyplot as plt  #plot library to show our data

import matplotlib.patches as patches

import time

import csv #import the comma separated package

arduinoSerialData = serial.Serial(‘com16’,9600) #Create Serial port object called arduinoSerialData

AQnum=[] #vector of PM numbers

AQcat=[] #list of categories

t = [0] # the time vector

icat=0 #the index of data categories

keepchecking4newcats=True #see if it’s the first time cathering categories of PM data

plt.close(“all”)  #close all open plots

fig, ax = plt.subplots()  #open a new figure in which we will plot

ax.grid() #display a grid on the plot

plt.ion() #starts interactive plot mode, so we can have an animated plot

ax.set_xlim(0, 100)#initial x limits

ax.set_ylim(0, 100)#initial y limits

plt.xlabel(‘time (sec)’, fontsize=14)#x axis label with size 14 font

plt.ylabel(‘PM (‘+’$\mu$g’+’/$m^3$’+’)’, fontsize=14)#y-axis label with size 14 font

ax.tick_params(labelsize=14)#ticks on axis set to size 14 font

fig.canvas.draw()#draw the plot canvas

plt.show(block=False) #keeps the plot from tying up the command window

print(‘Starting…’) #forster healthy communication with your user

ymax=-float(“inf”)#min and max y axis for plot

ymin=float(“inf”)

lines=[] #where we’ll keep our lines for our plots

ymin=float(“inf”)#min and max for plot axis

ymax=-float(“inf”)

RectWidth=100 #width of rectangle for AQ index colors, should be big…

AQclrs=np.array([[0,1,0,.2],[1,1,0,.2],[1,.5,0,.3],[1,0,0,.3],[.7,0,1,.3],[.7,0,.5,.2],[.4,0,.2,.3]]) #green,yellow,orange,red,purple,maroon

AQlvls=[0,50,100,150,200,300,500,10000] #AQ index levels

LnClr=[[0,1,1,.8],[0,.8,.8,.8],[0,.5,.5,.8],[0.3,0.3,0.3,.8]]  #line colors

i=0

PMrange=[]  #the rectangles that show the AQ index colors

for clr in AQclrs:#add color ranges for AQ index

    rec=ax.add_patch( patches.Rectangle( (0, AQlvls[i]), RectWidth, AQlvls[i+1]-AQlvls[i], fc=AQclrs[i,:] )  )

    PMrange.append(rec)

    i+=1

   

tic = time.time() # get the starting time

toc = 0 #will contain the time since initial tic

AQData=np.zeros([5,]) #initialize the array of data

while (1==1):#loop until the user hit ctrl-c

    toc = time.time() – tic;  #measure the time

    try:#collect data until ctrl-c is used

        if (arduinoSerialData.inWaiting()>0): #board is ready to send info

            AQDataTxt = str(arduinoSerialData.readline()) #get the info from the board

            i1=AQDataTxt.index(‘\”) #find the first singl quote

            i2=AQDataTxt.index(‘\”,i1+1) #find the last singl quote

            AQDataTxt=AQDataTxt[i1+1:i2] #extract the string between the single quotes

            AQDataTxt=AQDataTxt.replace(‘\\r\\n’,”)#remove the return

            AQDataTxt=AQDataTxt.replace(‘\\x00’,”)#remove the NULL chars

            #print(AQDataTxt)

            AQDataSplit=AQDataTxt.split(‘\\t’) #split by the tab character

            if (len(AQDataSplit)==1): #no tabs, just print for user

                isdata=False #true only if it’s numerical data

                print(AQDataTxt)

            else:  #has tab, then it’s part of a data table

                try:  #see if it’s a string that would be an integer

                    int(AQDataTxt[0]) #it can be made into an integer

                    isdata=True  #then it is data

                except ValueError:  #if not then it’s the column header

                    isdata=False  

                    AQcat=AQDataSplit

                    icat=0 #counter for categories

                    for cat in AQcat:

                        print(‘{0:^10}’.format(cat),end=”)  #print the headers

                        if (icat>0): #avoid the time column when creating lines

                            li, = ax.plot([0], [0], color=LnClr[icat-1]) #defines a line, li and makes clear we’ll be adding to it with the comma

                            lines.append(li) #add a line to a vector of lines

                        icat+=1 #incriment counter for categories

                    print(”)  #create a newline

                    ax.legend(AQcat[1:-1]) #give a legend to the plot

                    ncat=len(AQcat) #number of categories

                    AQData=np.zeros([ncat,]) #initialize the array of data

                   

            if (isdata):

                AQnums=[int(elem) for elem in AQDataSplit] #conver string numbers to integers

                for num in AQnums: #loop through the numbers

                    print(‘{0:^10d}’.format(num),end=”)

                AQData=np.vstack([AQData,AQnums])

                print(”)  #a newline

                i=0

                if (max(AQnums)>ymax):

                    ymax=max(AQnums)

                if (min(AQnums)<ymin):

                    ymin=min(AQnums)  

                for line in lines:

                    if (i>0):

                        line.set_xdata(AQData[:,0]) #plot the new x data for this line

                        line.set_ydata(AQData[:,i]) #plot the new y data for this line

                    i+=1

                plt.xlim( [0, toc] ) #adjust x-axis limit

                i=0

                for clr in AQclrs:  #change the width of AQ color squares

                    PMrange[i].set_width(toc)

                    i+=1

                plt.ylim( [0, ymax] ) #adjust y-axis limit

                plt.draw() #draw the new plot

                plt.pause(0.1) #pause a bit so the plot can show

    except KeyboardInterrupt: #let us escape when we’re done, when ctrl-c pressed

        print(‘broke’)

        break #exit the while loop

arduinoSerialData.close()  #stop tying up the serial port

# SAVE THE DATA

f = open(‘PMdata.csv’, ‘wt’, newline=”)#open a file (this will overwrite every time)

writer = csv.writer(f)

writer.writerow( AQcat ) #write the header

for dataRow in AQData:

    writer.writerow( dataRow.tolist()) #write the data

f.close()
