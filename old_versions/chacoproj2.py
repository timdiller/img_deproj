
#Coded by Tim Diller from Dec 2010 - Mar 2011

from enthought.traits.api import * #HasTraits,on_trait_change
#from enthought.traits.api import Int,Float,Range,Array,Enum,Bool
from enthought.traits.ui.api import * #View,Group,Item
from enthought.traits.ui.menu import OKButton,CancelButton
#from enthought.chaco.chaco_plot_editor import ChacoPlotItem
from enthought.chaco.api import * #Plot, ArrayPlotData, jet
from enthought.enable.api import *
from enthought.chaco.tools.api import *
import numpy as np
#from projective import projective

class ChacoProj(HasTraits):
    """ Projections using interactive Chaco session """
    data_raw = Array(np.float)
    data_prc = Array(np.float)
    inv = Bool(True)
    theta = Float(0.)
    trim_xmin = Int()
    trim_xmax = Int()
    trim_ymin = Int()
    trim_ymax = Int()
    shift_x = Int(0)
    shift_y = Int(0)
    keyst_x = Float(0.)
    keyst_y = Float(0.)
    scale_x = Float(1.)
    scale_y = Float(1.)

    raw_plot=Instance(Plot)
    prc_plot=Instance(Plot)
    L_container = Instance(HPlotContainer)
    R_container = Instance(HPlotContainer)
    
    view1 = View(
        Group(
            Group(
                Item('L_container',
                     editor=ComponentEditor(),
                     width=400,
                     show_label=False),
                Group(
                    Item(name='inv'),
                    Item(name='theta'),
                    orientation = "horizontal"),
                Group(
                    Item(name='trim_xmin',label='X-min'),
                    Item(name='trim_xmax'),
                    orientation = "horizontal"),
                Group(
                    Item(name='trim_ymin'),
                    Item(name='trim_ymax'),
                    orientation = "horizontal"),
                Group(
                    Item(name='shift_x'),
                    Item(name='shift_y'),
                    orientation = "horizontal"),
                Group(
                    Item(name='keyst_x'),
                    Item(name='keyst_y'),
                    orientation = "horizontal"),
                Group(
                    Item(name='scale_x'),
                    Item(name='scale_y'),
                    orientation = "horizontal"),
                orientation="vertical",label='Raw Data'),#Raw Data grouping
            Group(#Final Image Grouping
                Item('R_container',editor=ComponentEditor(),show_label=False),
                 orientation="vertical",label='Final Data'),#Final Image grouping
            orientation="horizontal"),
        buttons = [OKButton,CancelButton])


    def calc_dimensions(self):
        """
        Based on the shape of the raw data, calculate the x and y
        arrays for the raw data. This only needs to be done at the
        initialization and when a new raw data file is loaded. """
        xdim=self.z_raw.shape[1]
        ydim=self.z_raw.shape[0]
        
        xs=np.arange(float(xdim))#/float(xdim) #these are the x's
        ys=np.arange(float(ydim))#/float(ydim) #these are the y's



        x, y = np.meshgrid(xs,ys)

        self.x_raw = x
        self.y_raw = y


    def _inv_changed(self):
        if self.inv:
            self.invert = -1.
        else:
            self.invert = 1.
        print "Changed trait, invert = %1.0f" %(self.invert)
        self.recalc()
        self.replot()

    def _theta_changed(Self):
        self.recalc()
        self.replot()
        
    def recalc(self):
        from projective import construct_transform_from_params as ctfp
        from projective import projective, projective2, resquare
        from numpy import savez
        
        self.T = ctfp(inv=self.invert,theta=self.theta)

        #[x_t,y_t] = projective(self.x_raw,self.y_raw,self.T)
        [x_t,y_t] = projective2(self.z_raw.shape[1],self.z_raw.shape[0],self.T)
        [x,y,z] =   resquare(x_t,y_t,self.z_raw,npts_dim=40)
        self.x_trans = x
        self.y_trans = y
        self.z_trans = z

        plotdata = self.trans_plot.ArrayPlotData(z_trans=z,x=x,y=y)
        self.trans_plot = Plot(plotdata)

        savez('tempsave.npz',x=x,y=y,z=z,x_t=x_t,y_t=y_t,z_raw=self.z_raw,T=self.T)

        print "recalc()"

    def replot(self):
        self.trans_plot.delplot('right_plot')
        ## self.trans_plot.contour_plot(
        ##     'z_trans',
        ##     name="right_plot",
        ##     type="poly",
        ##     y=self.x_trans, 
        ##     x=self.y_trans,
        ##     levels=128)
        self.trans_plot.request_redraw()

        print "replot()"

        
    def __init__(self):
        npz=np.load('savefile.npz')
        #self.z_trans=npz[npz.files[0]]
        self.z_raw=npz[npz.files[0]]
        self.invert=-1.
        self.calc_dimensions()
        self.recalc()

        pd = ArrayPlotData()
        pd.set_data('z_trans',self.z_trans)
        pd.set_data('z_raw',self.z_raw)
        #pd.set_data('x_data',self.x_raw)
        #pd.set_data('y_data',self.y_raw)

        lplot = Plot(pd)
        lplot.contour_plot(
            'z_raw',
            name="left_plot",
            type="poly",
            levels=128)
        self.raw_plot = lplot
        self.left_renderer = self.raw_plot.plots['left_plot'][0]
        
        rplot = Plot(pd)
        rplot.contour_plot(
            'z_trans',
            name="right_plot",
            type="poly",
            y=self.x_trans, 
            x=self.y_trans,
            levels=128)
        self.trans_plot = rplot
        self.right_renderer = self.trans_plot.plots['right_plot'][0]
        
        lcont = HPlotContainer()
        lcont.add(lplot)
        rcont = HPlotContainer()
        rcont.add(rplot)
        self.L_container = lcont
        self.R_container = rcont

    def start(self):
        ##plotdata = ArrayPlotData(data_raw = npz[npz.files[0]])
        ## plot = Plot(plotdata)
        ## plot.img_plot("imagedata", colormap=jet)
        ## self.plot = plot

        ##self._perform_calculations()
        self.configure_traits()


f=ChacoProj()
f.start()
