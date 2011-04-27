def loadfluentxy(filename=''):
    """
    data = loadfluentxy(filename='')
    
    Tor loading data from Fluent solution export, which is tab
    delimited and has 1 header line. The columns follow a general form
    in which the first three columns are node number and x- and y-
    coordinates. The value of the exported variable(s) follow in the
    subsequent column(s). In the present implementation, import of
    only one column is supported.
    The names of the data columns are contained in the data structure
    returned:
    data.dtype.names
    returns a list of the vairiables available
    """
    
    import numpy as np
    from datetime import datetime
    from StringIO import StringIO
    import Tkinter
    from tkFileDialog import askopenfilename
    import progressbar as pb

    if (filename):
        print "Opening %s..." %(filename)
    else:
        root = Tkinter.Tk()
        root.withdraw()
        filename=askopenfilename(parent=root,title='Open File')
        root.destroy()
        root.mainloop()

    if (filename):
        f=open(filename)
        d = np.genfromtxt(f, delimiter = ',', unpack = True, names = True)
        print "Found the following columns:"
        print d.dtype.names
        f.close()
        return d

def loadROIfile(filename=''):
    """
    data = loadROIfile(filename='')
    for loading data from FLIR ExaminIR, which is tab delimited, and
    has 1 header line with vairable names
    the names of the data columns are contained in the data structure
    time is assumed to be in the second column and is parse
    returned:
    data.dtype.names
    returns a list of the vairiables available
    """

    import numpy as np
    from datetime import datetime
    from StringIO import StringIO
    import Tkinter
    from tkFileDialog import askopenfilename
    import progressbar as pb
#    from matplotlib.pyplot import figure,subplot,plot,xlabel,ylabel,title,legend

    if (filename):
        print "Opening %s..." %(filename)
    else:
        root = Tkinter.Tk()
        root.withdraw()
        filename=askopenfilename(parent=root,title='Open File',filetypes=[('text files','*.txt')])
        root.destroy()
        root.mainloop()

    if (filename):
        f=open(filename)
        #d = np.genfromtxt(f,delimiter='\t',unpack=True,names=True)
        d = np.genfromtxt(f,delimiter='\t',unpack=True,names=True,dtype="i8,S25,f8,f8,f8,S8")
        t = datetime.strptime(d['time'][0],"%Y-%m-%d %H:%M:%f00")
        time=np.zeros(len(d))
        t0 = 1e-4*t.microsecond + 60*t.minute + 3600*t.hour + 24*3600*t.day
        print "\nParsing time strings...\n"
        pbar=pb.ProgressBar().start()
        len_d=float(len(d))
        for i in range(1,len(d)):
            t = datetime.strptime(d['time'][i],"%Y-%m-%d %H:%M:%f00")
            time[i] =  1e-4*t.microsecond + 60*t.minute + 3600*t.hour + 24*3600*t.day - t0
            pbar.update(100.*float(i)/len_d)
        pbar.finish()
        f.close()
        return d,time

def loadxy(filename=''):
    """data = loadxy(filename='')
    for loading x-y data from Fluent, which is tab delimited, has 4 header lines and one footer line
    this function does not return names, only data
"""
    import numpy as np
    from StringIO import StringIO
    import Tkinter
    from tkFileDialog import askopenfilename
#    from matplotlib.pyplot import figure,subplot,plot,xlabel,ylabel,title,legend

    if (filename):
        print "Opening %s\n" %(filename)
    else:
        root = Tkinter.Tk()
        root.withdraw()
        filename=askopenfilename(parent=root,title='Open File',filetypes=[('xy files','*.xy')])
        root.destroy()
        root.mainloop()

    if (filename):
        f=open(filename)
        d = np.genfromtxt(f,delimiter='\t',unpack=True,skip_header=4,skip_footer=1)
        s = argsort(d)
        data = d[:,s[0]]
        return data

        
def loadXLcsv():
    """
    Imports a csv file produced by MS Excel
    MS Excel files written as .csv have \r at the end of lines instead of the more typical \r\n
"""
    import numpy as np
    from StringIO import StringIO
    import Tkinter
    from tkFileDialog import askopenfilename
#    from matplotlib.pyplot import figure,subplot,plot,xlabel,ylabel,title,legend

    root = Tkinter.Tk()
    root.withdraw()
    filename=askopenfilename(parent=root,title='Open File',filetypes=[('csv files','*.csv')])
    root.destroy()
    if(filename):
        f=open(filename)

    if(f):
        l = f.read() #because there are no \n's this will read the whole file.
        f.close()
        s = StringIO(l.replace('\r','\n'))#write the string into a virtual file
        names = s.readline()#strip the header line
        names = names.strip('\n')
        names = names.split(",")

        data = np.genfromtxt(s,delimiter=',',unpack=True)
        return data,names

def loadtcdat(filename=''):
    """
    loads csv data written by Fluent as part of the output.
    These files are specific to 2D simulation runs during the post-doc research of Tim Diller.
    the file is called 'tcdat.csv'
"""
    import numpy as np
    from StringIO import StringIO
    import Tkinter
    from tkFileDialog import askopenfilename
    from matplotlib.pyplot import figure,subplot,plot,xlabel,ylabel,title,legend

    if (filename):
        print "Opening %s\n" %(filename)
    else:
        root = Tkinter.Tk()
        root.withdraw()
        filename=askopenfilename(parent=root,title='Open File',filetypes=[('csv files','*.csv'),('txt files', '*.txt')])
        root.destroy()
        root.mainloop()

    if (filename):
        f=open(filename)
        names = f.readline() #variable names
        names = names.strip('\r\n')
        names = names.split(",")
        f.close()

        data = np.genfromtxt(filename,delimiter=',',unpack=True,skip_header=2)
        time = data[0]

        figure()
        subplot(211)
        plot(time,data[1],label='Feed bin')
        plot(time,data[2],label='Part bin')
        ylabel(r'$ T_{bin} \left(K\right) $')
        legend(loc='best')

        subplot(212)
        plot(time,data[4],label='Feed bin heater')
        plot(time,data[5],label='Part bin heater')
        xlabel(r'$ Time \left(s\right) $')
        ylabel(r'$ P_{heater} \left( \frac{W}{m^2} \right) $')
        legend(loc='best')

        return (data,time,names)
    else:
        return
    
def loadSS2500(filename=''):
    """
    (data,time,names) = loadSS2500()
    This reads the data file produced by the operating program in the SinterStation2500.
    It automatically imports the data and plots the part bin surface temperature and
    part bin heater intensity as a function of time.
"""
    import numpy as np
    from StringIO import StringIO
    import Tkinter
    from tkFileDialog import askopenfilename
    from matplotlib.pyplot import figure,subplot,plot,xlabel,ylabel,title,legend

    if (filename):
        print "Opening %s\n" %(filename)
    else:
        root = Tkinter.Tk()
        root.withdraw()
        filename=askopenfilename(parent=root,title='Open File',filetypes=[('csv files','*.csv'),('txt files', '*.txt')])
        root.destroy()
        root.mainloop()

    if(filename):
        f=open(filename)
        
        names = f.readline() #variable names
        names = names.strip('\r\n')
        names = names.split("\t")
        f.close()

        print('removing \'' + names.pop(0) + '\' from names list\n')
        print('removing \'' + names.pop(0) + '\' from names list\n')

        cols=np.arange(2,len(names))
        data = np.genfromtxt(filename,delimiter='\t',unpack=True,skip_header=1,usecols=cols)
        timestrings = np.genfromtxt(filename,delimiter='\t',unpack=True,skip_header=1,usecols=[1],dtype=str)
        time = np.zeros(len(timestrings))

        for i in range(len(timestrings)):
            s = StringIO(timestrings[i])
            timedata = np.genfromtxt(s,dtype=[int,int,float],delimiter=":")
            (hours,minutes,seconds) = timedata.item()
            time[i] = 3600.*hours + 60.*minutes + seconds

        PBT = names.index('Part Bed Temp.')
        PBDC = names.index('Part Bed  Duty Cycle')

        figure()
        subplot(211)
        #title(filename)
        plot(time,data[PBT],label=names[PBT])
        ylabel(names[PBT] + r'$ \left(^{\circ}C\right)$')

        subplot(212)
        plot(time,data[PBDC],label=names[PBDC])
        xlabel('Time(s)')
        ylabel(names[PBDC] + r'$ \left( \% \right) $')

        return data,time,names
    else:
        return
    
def PIDdata(time,temperature,setp):
    """
    PIDdata(time,temperature,setp)
    User interface tool to open file and provide inital plot of the results
"""
    from scipy import polyfit
    from matplotlib.pyplot import figure,subplot,plot,xlabel,ylabel,title

    l=len(temperature)
    Pdat = zeros(l)
    Idat = zeros(l)
    Ddat = zeros(l)

    Pdat[0] = setp-temperature[0]
    for i in range(1,l):
        epsilon = setp - temperature[i]
        Pdat[i] = epsilon
        Idat[i] = Idat[i-1] + epsilon

    for i in range(2,l-2):
        j=range(i-2,i+3)
        (a,b)=polyfit(time[j],temperature[j],1)
        Ddat[i] = a

    figure()
    subplot(411)
    plot(time,temperature)
    ylabel(r'Temperature $ \left( ^{\circ} C \right) $')
    subplot(412)
    plot(time,Pdat)
    ylabel(r'$ \epsilon = T_{set}-T_{meas} \left( ^{\circ}C \right) $')
    subplot(413)
    plot(time,Idat)
    ylabel(r'$ \int_0^t \epsilon dt $')
    subplot(414)
    plot(time,Ddat)
    xlabel('Time (s)')
    ylabel(r' $ \frac{d \epsilon}{dt} $')

    return Pdat,Idat,Ddat


def loadIRframe(f):
    """
    frame = loadIRframe(f)
    this function is to load one frame from a large .csv file from the IR camera.
    The format is semicolon separated temperature values (C), each row of 320 values
    separated by a \n character.
    Pass this function a pointer to the csv file.
"""
    import numpy as np
    from StringIO import StringIO
    frame = np.zeros((240,320),dtype=float)
    for i in range(240):
        s=StringIO(f.readline())
        if s:
            frame[i]=np.genfromtxt(s,delimiter=';')
        else:
            print('Did not load the line.\n')
            return 0
    return frame#[35:195,80:260]        

def loadIRcsv(f):
    """
    frame = loadIRcsv(f)
    this function is to load one frame from a  .csv file from the IR camera.
    The format is comma separated temperature values (C), each row of 320 values
    separated by a \r\n character.
    Pass this function a pointer to the csv file.
"""
    import numpy as np
    from StringIO import StringIO
    frame = np.zeros((240,320),dtype=float)
    for i in range(240):
        l=f.readline()
        s=StringIO(l.strip('\r\n'))
        if s:
            frame[i]=np.genfromtxt(s,delimiter=',')
        else:
            print('Did not load the line.\n')
            return 0
    return frame#[35:195,80:260]        

def IR2mov():
    import numpy as np
    from StringIO import StringIO
    import Tkinter
    from tkFileDialog import askopenfilename
    import os

    root = Tkinter.Tk()
    root.withdraw()
    filename=askopenfilename(parent=root,title='Open File',filetypes=[('csv files','*.csv')])
    root.destroy()
    i=0
    go = 1
    if(filename):
        f=open(filename)
        (root,ext)=os.path.splitext(filename)
        (x, name) = os.path.split(root)
    if(f):
        while go:
            frame=loadIRframe(f)
            if(frame.any):
                i+=1
                fname=('img/%s%03d.png') %(name,i)
                imsave(fname,frame,format='png')
            else:
                go=0
        
def IRsplit():
    import numpy as np
    from StringIO import StringIO
    import Tkinter
    from tkFileDialog import askopenfilename
    import os

    root = Tkinter.Tk()
    root.withdraw()
    filename=askopenfilename(parent=root,title='Open File',filetypes=[('csv files','*.csv')])
    root.destroy()
    i=0
    go = 1
    if(filename):
        f=open(filename)
        (root,ext)=os.path.splitext(filename)
        (x, name) = os.path.split(root)
        dirname=('%sdat') %name
        os.mkdir(dirname)
    if(f):
        while go:
            frame=loadIRframe(f)
            if(frame.any):
                i+=1
                fname=('%s/%s%03d.npy') %(dirname,name,i)
                save(fname,frame)
            else:
                go=0
