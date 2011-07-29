from traits.api import * 
from traitsui.api import * #View,Group,Item
from traitsui.menu import OKButton,CancelButton
from chaco.api import * #Plot, ArrayPlotData, jet
from enable.api import *
from chaco.tools.api import *
import numpy as np
import wx
import matplotlib as mpl
mpl.use('WXAgg',warn=False)

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from traitsui.wx.editor import Editor
from traitsui.wx.basic_editor_factory import BasicEditorFactory

class _MPLFigureEditor(Editor):
    """
    MPLFigureEditor is an Editor object that allows the use of
    matplotlib figures in a Traits UI environment.
    In this case, it is necessary because the matplotlib contour()
    function handles missing data and plots xyz data in a way that
    causes problems for the Chaco contour plotting function.
    Code was copied in February 2011 from
    from http://github.enthought.com/traits/tutorials/traits_ui_scientific_app.html
    """
    scrollable  = True

    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self):
        pass

    def _create_canvas(self, parent):
        """ Create the MPL canvas. """
        # The panel lets us add additional controls.
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        # matplotlib commands to create a canvas
        mpl_control = FigureCanvas(panel, -1, self.value)
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
        toolbar = NavigationToolbar2Wx(mpl_control)
        sizer.Add(toolbar, 0, wx.EXPAND)
        self.value.canvas.SetMinSize((10,10))
        return panel

class MPLFigureEditor(BasicEditorFactory):
    klass = _MPLFigureEditor


class ChacoProj(HasTraits):
    """ Projections using interactive Chaco session
    Coded by Tim Diller from Dec 2010 - Mar 2011
    Version history --------------------------------------------------
        v0.1 saved 24 March 2011
         - has a single working contour to display transformed data
        v0.2 saved 25 March 2011
         - has two contour plots and new buttons to show raw and
           transformed data.
         - recalculation is performed at user initiation through a
           button rather than on the update of any widget value. This
           prevents lengthy recalculations after each keystroke.
        v0.3 saved 29 March 2011
         -cleaned up comments and blocked out code.
         -griddata() fails with a memory error during the rotation
          operation
        v0.4 saved 30 March 2011
         -implement matplot figure within TraitsUI so that the contour
          plotting works without needing griddata()
         -works, but it's ugly.
        v0.5
         -clean up from v.04 and simplify UI
         -single recalc button
         -bring projective calcs into this class
        v0.6
         -add file open
         -add plot to preview to show display quadrilaterals

    figure = Instance(Figure,()) behaves similarly to figure=figure()
    would in matplotlib. Thus figure is a handle to the figure object
    embedded in the Traits UI.
    """
    ## UI elements
    inv = Bool(True)
    units = Enum('K','C',desc = 'units of original data')
    theta = Float(0.0,desc='degrees')
    gridsize = Int(20,desc='pixel size of recalculated image')
    trim_xmin = Int(0, desc = 'pixel position of left edge of raw image')
    trim_xmax = Int(10,desc = 'pixel position of right edge of raw image')
    trim_ymin = Int(0, desc = 'pixel position of bottom edge of raw image')
    trim_ymax = Int(10,desc = 'pixel position of top edge of raw image')
    shift_x = Float(0,desc = 'location of center in raw data units')
    shift_y = Float(0,desc = 'location of image bottom in raw data units')
    keyst_x = Float(0.0, desc = ' typical value is 0')
    keyst_y = Float(0.0, desc = 'keystone correction. typical value is -0.01')
    scale_x = Float(1.)
    scale_y = Float(1.)
    ax_xmin = Float(-150.)
    ax_xmax = Float(150.)
    ax_ymin = Float(0.)
    ax_ymax = Float(300.)

    recalc_button = Button()
    load_button = Button()

    data_file = File(filter = ['csv','npz'])
    
    raw_plot=Instance(Plot)
    L_container = Instance(HPlotContainer)
    figure = Instance(Figure, ())
    
    view1 = View(
        Group(
            Group(
                Group(
                    Item('L_container',
                         editor = ComponentEditor(),
                         width = 400,
                         show_label = False),
                    Group(
                        Item(name = 'trim_xmin',label = 'min'),
                        Item(name = 'trim_xmax',label = 'max'),
                        orientation = "horizontal",
                        label = 'X Clipping'),
                    Group(
                        Item(name = 'trim_ymin',label = 'min'),
                        Item(name = 'trim_ymax',label = 'max'),
                        orientation = "horizontal",
                        label = 'Y Clipping'),
                    Group(
                        Item(name='shift_x',label='X'),
                        Item(name='shift_y',label='Y'),
                        label = "Offset",
                        orientation = "horizontal"),
                    Group(
                        Item(name = 'inv'),
                        Item(name = 'theta'),
                        Item('units',label = 'Units'),
                        orientation = "horizontal"),
                    orientation="vertical",label='Raw Data'),#Raw Data grouping
                Group(
                    Item('figure',
                         editor = MPLFigureEditor(),
                         width = 400,
                         height = 400,
                         show_label = False),
                    Group(
                        Item(name='keyst_x'),
                        Item(name='keyst_y'),
                        orientation = "horizontal"),
                    Group(
                        Item(name='scale_x'),
                        Item(name='scale_y'),
                        orientation = "horizontal"),
                    Group(
                        Group(
                            Item(name = 'ax_xmin',label = 'x-',format_str="%.1f"),
                            Item(name = 'ax_xmax',label = 'x+',format_str="%.1f"),
                            orientation = "vertical"),
                        Group(
                            Item(name = 'ax_ymin',label = 'y-',format_str="%.1f"),
                            Item(name = 'ax_ymax',label = 'y+',format_str="%.1f"),
                            orientation = "vertical"),
                        orientation = "horizontal",
                        label = 'Axis'),
                    orientation="vertical",
                    label='Final Data'),
                orientation="horizontal"),
            Group(
                Item(name = 'data_file'),
                Item('load_button',
                     label = 'Load',
                     show_label = False),
                Item('recalc_button',
                     label = 'Recalculate',
                     show_label = False),
                orientation = "horizontal"),
            orientation = "vertical"),
        title = "Deprojection Tool",
        buttons = [OKButton])

    def generic_init(self):
        #self.calc_dimensions()
        self.clip_data()
        self.recalc()
        self.shift_x = int(np.mean(self.x_raw[0]))
        #self.shift_y = int(-1*max(np.ceil(self.y_raw[:,0])))

        self.pd.set_data('z_raw',self.z_clip)

    def __init__(self):
        """
        need to change this to offer a load dialog on startup. for
        development and debugging, just load the data from an npz
        save file.

        axes are added to the figure here under the handle self.axes.
        
        """
        ## npz=np.load('savefile.npz')
        ## self.z_raw  = npz[npz.files[0]]
        ## self.pd.set_data('z_trans',self.z_trans)

        x = np.linspace(-np.pi,np.pi,100)
        y = np.linspace(-np.pi/2.,3.*np.pi/2.,100)
        [X,Y] = np.meshgrid(x,y)
        self.z_raw = np.sin(X)*np.cos(Y)
        self.x_raw = X
        self.y_raw = Y
        self.trim_xmax=self.z_raw.shape[1]
        self.trim_ymax=self.z_raw.shape[0]

        self.pd = ArrayPlotData()
        self.generic_init()
        
        lplot = Plot(self.pd)
        lplot.contour_plot(
            'z_raw',
            xbounds = (min(self.x_raw[0]),  max(self.x_raw[0])),
            ybounds = (min(self.y_raw[:,0]),max(self.y_raw[:,0])),
            name="left_plot",
            type="poly",
            levels=128)
        self.l_plot = lplot
        self.left_renderer = self.l_plot.plots['left_plot'][0]
        lcont = HPlotContainer()
        lcont.add(lplot)
        self.L_container = lcont
        
        self.axes = self.figure.add_subplot(111)

    def clip_data(self):
        """
        Take the raw data and clip it to size.
        Check for offset errors. Negative y coordinates cause divide
        by zero errors.
        """
        #from matplotlib.mlab import griddata 1
        self.x_clip = self.x_raw[self.trim_ymin:self.trim_ymax,
                                 self.trim_xmin:self.trim_xmax]
        self.y_clip = self.y_raw[self.trim_ymin:self.trim_ymax,
                                 self.trim_xmin:self.trim_xmax]
        self.z_clip = self.z_raw[self.trim_ymin:self.trim_ymax,
                                 self.trim_xmin:self.trim_xmax]

        if self.inv:
            inv = (1-2*self.inv)
            if inv*self.shift_y < max(self.y_clip[:,0]):
                self.shift_y = inv*max(self.y_clip[:,0])
        #else:
            #if self.shift_y >  min(self.y_clip[:,0]):
            #self.shift_y = min(self.y_clip[:,0])

    def calc_dimensions(self):
        """
        Based on the shape of the raw data, calculate the x and y
        arrays for the raw data. This only needs to be done at the
        initialization and when a new raw data file is loaded.
        sets x_raw and y_raw based on the dimension of z_raw
        """
        xdim=self.z_raw.shape[1]
        self.trim_xmax=xdim
        ydim=self.z_raw.shape[0]
        self.trim_ymax=ydim
        xs=np.arange(float(xdim))#/float(xdim) #these are the x's
        ys=np.arange(float(ydim))#/float(ydim) #these are the y's
        x, y = np.meshgrid(xs,ys)

        self.x_raw = x
        self.y_raw = y

    def _inv_changed(self):
        if self.inv:
            self.shift_y = -1*self.trim_ymax
        else:
            self.shift_y = self.trim_ymin

    def _load_button_fired(self):
        from os.path import splitext

        def npz_open():
            npz = np.load(self.data_file)
            if len(npz.files) > 1:
                print "Using first saved array in '" + self.data_file + "'"
            return npz[npz.files[0]]
            
        def csv_open():
            f=open(self.data_file)
            return(np.genfromtxt(f,delimiter=','))

        fileopen = {'.npz':npz_open,
                    '.csv':csv_open,
                    }
        self.z_raw = fileopen[splitext(self.data_file)[1]]()
        self.calc_dimensions()
        self.generic_init()

        self.l_plot.delplot('left_plot')
        self.l_plot.contour_plot(
            'z_raw',
            name="left_plot",
            type="poly",
            y=self.x_raw, 
            x=self.y_raw,
            levels=128)
        self.l_plot.request_redraw()
        
    def _recalc_button_fired(self):
        self.clip_data()
        self.recalc()
        self.replot()
        
    def recalc(self):
        """
        Take the clipped data and apply the rotation, keystone, and
        scaling operations.
        """
        from projective import construct_transform_from_params as ctfp
#        from projective import projective, projective2, resquare
#        from numpy import savez
        offset={'K':-273.,'C':0.}

        T = ctfp(inv = (1-2*self.inv),
                 theta = self.theta,
                 kx = self.keyst_x, ky = self.keyst_y,
                 sx = self.scale_x, sy = self.scale_y,
                 tx = self.shift_x, ty = self.shift_y)

        xy1=np.asarray([np.resize(self.x_clip,np.size(self.x_clip)),
                        np.resize(self.y_clip,np.size(self.y_clip)),
                        np.ones(np.size(self.x_clip))])

        U=np.dot(xy1.T,T)

        del xy1

        u=U[:,0]
        v=U[:,1]
        w=U[:,2]

        del U

        x2=u/w
        y2=v/w

        self.x_trans = np.resize(x2,self.x_clip.shape)
        self.y_trans = np.resize(y2,self.y_clip.shape)
        self.z_trans = self.z_clip + offset[self.units]

        #print offset[self.units]

        del x2,y2#,z2

#        savez('tempsave.npz',x=x,y=y,z=z,x_t=x_t,y_t=y_t,T=self.T)

    def replot(self):
        """
        Any time there is an update to the transformed data, update
        the contour plot in the right-hand container.
        This function refers solely to data stored in the ChacoProj
        class.
        matplotlib contour() plots the lines, and contourf() fills
        in between the lines, so calls to both are necessary to get
        a solid image.

        self.figure is the handle to the figure object
        self.axes is the handle to the axes
        Both of these are set up in the __init__() function.
        """
        self.axes.cla()
        c1=self.axes.contourf(self.x_trans,
                              self.y_trans,
                              self.z_trans,
                              128,
                              cmap=mpl.cm.gray,
                              antialiased=False)
        c2=self.axes.contour(self.x_trans,
                             self.y_trans,
                             self.z_trans,
                             128,
                             cmap=mpl.cm.gray)
        self.axes.set_xlim((self.ax_xmin,self.ax_xmax))
        self.axes.set_ylim((self.ax_ymin,self.ax_ymax))

        #Update the color bar. Check first whether it's been
        #instantiated yet.
        try:
            self.cb.ax.cla()
            self.cb = self.figure.colorbar(c1,self.cb.ax)
        except AttributeError:
            self.cb = self.figure.colorbar(c1)

        unitstring={'K':'(K)','C':'($ ^{\circ} $C)'}
   
        self.cb.set_label(r'Temperature %s' %(unitstring[self.units]))
        self.figure.canvas.draw()

    def start(self):
        self.configure_traits()


f=ChacoProj()
f.start()
