def errproj(T_try,xy,x2y2):
    """Return the Euclidian distance between T(xy) and x2y2.
    where T() is a tuple of the eight fitable members of a
    transformation matrix.
    This is the minimizeable function for determining the
    transformation T to map xy to x2y2.
    """
    from scipy import sum, resize, asarray, sqrt
    T=asarray(resize(T_try+(1,),(3,3)))#array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
    [x2,y2]=projective(xy[0],xy[1],T)
    return sqrt(sum((x2y2[0]-x2)**2) + sum((x2y2[1]-y2)**2))

def projective(x,y,T):
    """Transform two arrays of points x,y into 1XN arrays of points
    x2,y2 according to the 3X3 transformation array T.
    """
    from scipy import outer, ones, arange, resize, dot, asarray, size
    try:
        cont=(T.shape==(3,3))
    except AttributeError:
        print 'T must be of ndarray or matrix type.'
        return

    if not(cont):
        print "T must be of dimension (3,3)"
    
    #data = load('/Users/tim/Documents/SFF_Thermal_Model/B3Sintdat/B3Sint001.npy')

    #xdim = data.shape[1]
    #ydim = data.shape[0]
    #x=outer(ones(ydim),arange(xdim))
    #y=outer(arange(ydim),ones(xdim))

    z=asarray([resize(x,size(x)),resize(y,size(y)),ones(size(x))])

    U=dot(z.T,T)

    u=U[:,0]
    v=U[:,1]
    w=U[:,2]

    #reshape to original size
    x2=resize(u/w,x.shape)
    y2=resize(v/w,y.shape)

    return x2,y2

def projective2(xdim,ydim,T):
    """Given the x dimension (xdim) and y dimension (ydim) of an image,
    produce two arrays [ydim,xdim] of the x and y coordinates
    according to the 3X3 transformation array T.
    """
    
    from scipy import outer, ones, arange, resize, dot, asarray, size
#    from numpy import *
    
    if(T.shape<>(3,3)):
        print 'T must be a 3X3 array or matrix.'
        return

    #data = load('/Users/tim/Documents/SFF_Thermal_Model/B3Sintdat/B3Sint001.npy')

    #xdim = data.shape[1]
    #ydim = data.shape[0]
    x=outer(ones(ydim),arange(xdim))
    y=outer(arange(ydim),ones(xdim))

    z=asarray([resize(x,size(x)),resize(y,size(y)),ones(size(x))])

    U=dot(z.T,T)

    u=U[:,0]
    v=U[:,1]
    w=U[:,2]

    x2=resize(u/w,(ydim,xdim))
    y2=resize(v/w,(ydim,xdim))

    return x2,y2

def plotproj(data,T,pb=False):
    """
    plotproj(data,T)
    Plots array 'data' transformed by transformation
    T, a 3X3 array.
    The dimensions [N,M] of T are calculated automatically and NXM arrays x an y
    are returned from this function
    """
    import scipy
    from scipy import size
    from matplotlib import pyplot as plt
    xdim = data.shape[1]
    ydim = data.shape[0]
    [x,y]=projective2(xdim,ydim,T)
    plt.figure(1,figsize=(6,4))
    plt.cla()
    plt.contour(x,y,data,128)
    plt.contourf(x,y,data,128)
    plt.grid(True)
    if(pb):
        plt.axis((-240.,240.,0.,350.))
        plt.ylabel('Y Position (mm)')
        plt.xlabel('X Position (mm)')
    return x,y
    
#def trans(data,inv=-1.,theta=0.7,tx=90.,ty=-70,kx=0.,ky=-0.01,sx=1.,sy=1.,pb=False):
def construct_transform_from_params(inv=-1.,theta=0.0,tx=0.,ty=0,kx=0.,ky=0.,sx=1.,sy=1.):
    """
    T=construct_transform_from_params(inv,theta,tx,ty,kx,ky,sx,sy)
    construct_transform_from_params() accepts transformation
    parameters and returns a 3X3 transformation matrix T
    
    inv - -1 applies a vertical inversion to the image
    theta - angle of rotation in degrees sign in the mathematical
            sense: theta > 0 -> CCW
    tx - horizontal pixel center of the image tx > 0 shifts origin right
         typical value ~95
    ty - horizontal pixel center of the image
         if inv = -1, then ty < 0 shifts the origin down
         typical value ~-65
    kx - keystone correction x
         typical value 0
    ky - keystone correction y
         typical value -0.01
    sx - scale x - xdimension of the field of view
    sy - scale y - ydimension of the field of view
    """

    import scipy
    from scipy import dot, cos, sin, pi
    from matplotlib import pyplot as plt
    from scipy import asarray

    theta_rad = theta*pi/180.
    
    #inversion transform I
    I=asarray([[1.,0.,0.],
               [0,inv,0.],
               [0.,0.,1.]])
    #displacement transform D
    D=asarray([[1.,0.,0.],
               [0.,1.,0.],
               [-tx,-ty,1.]])
    #rotation transform R
    R=asarray([[cos(theta_rad),sin(theta_rad),0.],
               [-sin(theta_rad),cos(theta_rad),0.],
               [0.,0.,1.]])
    #keystone transform K
    K=asarray([[1.,0.,kx],
               [0.,1.,ky],
               [0.,0.,1.]])
    #scale transform S
    S=asarray([[sx, 0., 0.],
               [0., sy, 0.],
               [0., 0., 1.]])

    #combine all the transforms, in order
    T=dot(dot(dot(dot(I,D),R),K),S)
    return T

def resquare(x,y,z,npts_dim=20):
    import numpy as np
    from scipy.interpolate import griddata

#    npts_dim = 20 #number of points per dimension

    #npz=load('savefile.npz')
    #z=npz[npz.files[0]]

    xmin=0.
    xmax=180
    ymin=0.
    ymax=-70.

    xdim=z.shape[1]
    ydim=z.shape[0]

#    x2=np.outer(np.ones(ydim),np.arange(xmin,xmax,(xmax-xmin)/xdim))
#    y2=np.outer(np.arange(ymin,ymax,(ymax-ymin)/ydim),np.ones(xdim))

    x2=np.outer(np.ones(npts_dim),np.linspace(x.min(),x.max(),npts_dim))
    y2=np.outer(np.linspace(y.min(),y.max(),npts_dim),np.ones(npts_dim))


    x2_p=np.resize(x2,np.size(x2))
    y2_p=np.resize(y2,np.size(y2))
    x_p=np.resize(x,np.size(x))
    y_p=np.resize(y,np.size(y))
    z_p=np.resize(z,np.size(z))
    
    grid_z = griddata((x_p,y_p),z_p,(x2_p,y2_p),method='linear')

    return x2,y2,np.resize(grid_z,x2.shape)
