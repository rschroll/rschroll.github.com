import os
from numpy import loadtxt, zeros, r_, sqrt, cross, dot
from numpy.linalg import norm
from pylab import find
import plot3D
import new
#from enthought.mayavi import mlab
#from pylab import load

class BaseSurf():
    """A base class for abstracting surfaces.  Contains everything except
    load() and associated calc_* routines."""
    
    def __init__(self, filename=None, mirror=False):
        if filename:
            self.load(filename)
        self.mirror = mirror
        self.plot_stretch = new.instancemethod(_make_plotting_func(self.stretch_density, "Stretching"), self)
        self.plot_bend = new.instancemethod(_make_plotting_func(self.bend_density, "Bending"), self)
        self.plot_height = new.instancemethod(_make_plotting_func(lambda: self.f_z, "Height"), self)
    
    def load(self, filename):
        raise NotImplementedError, "Descendants must implement a load method!"
    
    def calc_area(self):
        self.f_area = r_[[norm(cross(self.verts[f[1],:]-self.verts[f[0],:],
                                     self.verts[f[2],:]-self.verts[f[0],:]))
                          for f in self.facets]]
    
    def bend_density(self):
        return self.f_bend / self.f_area
    
    def stretch_density(self):
        return self.stretch / self.f_area
    
    def plot_all(self, title=None, **kw):
        p = plot3D.plt
        p.figure()
        p.subplot(131)
        self.plot_height(colorbar=True, **kw)
        p.subplot(132)
        self.plot_stretch(colorbar=True, **kw)
        p.subplot(133)
        self.plot_bend(colorbar=True, **kw)
        p.subplot(132)
        if title:
            p.title(title)

def _make_plotting_func(pltval, label):
    def plot_function(self, threeD=False, colorbar=False, **kw):
        kw['mirror'] = self.mirror
        if threeD:
            pltfunc = plot3D.plot_trimesh
        elif colorbar:
            pltfunc = plot3D.plot_trimesh2D_cb
            kw["label"] = label
        else:
            pltfunc = plot3D.plot_trimesh2D
        pltfunc(self.verts, self.facets, pltval(), **kw)
    return plot_function

class EvolveSurf(BaseSurf):
    """Abstracting a surface from Surface Evolver."""
    
    def load(self, filename):
        d = loadtxt(filename)
        self.nv, self.nf = d[0,:2]
        self.verts = d[1:self.nv+1,:3]
        self.bend  = d[1:self.nv+1, 3]
        self.ref_coords = d[1:self.nv+1, 4:]
        self.facets = d[self.nv+1:,:3] - 1 # SE is 1-indexed
        self.stretch = d[self.nv+1:, 3]
        self.form_factors = d[self.nv+1:, 4:]
        self.f_bend = r_[[sum([self.bend[ind] for ind in face])/3 
                           for face in self.facets]]
        self.f_z = r_[[sum([self.verts[ind,2] for ind in face])/3
                        for face in self.facets]]
        self.calc_area()
    
#    def plotbend(self, **kw):
#        mlab.triangular_mesh(self.verts[:,0], self.verts[:,1], self.verts[:,2], 
#                             self.facets[:,:3]-1, scalars=self.verts[:,3], **kw)
#    
#    def plotstretch(self, **kw):
#        pts = zeros((3*self.nf, 3))
#        vals = zeros(3*self.nf)
#        for i in range(self.nf):
#            for j in range(3):
#                pts[3*i+j,:] = self.verts[self.facets[i,j]-1, :3]
#                vals[3*i+j] = self.facets[i,3]
#        mlab.triangular_mesh(pts[:,0], pts[:,1], pts[:,2], 
#                             arange(3*self.nf).reshape((-1,3)),
#                             scalars=vals, **kw)

class MinSurf(BaseSurf):
    """Abstracting a surface from the membrane minimizer code."""
    
    def load(self, filename):
        self.verts = loadtxt(filename)
        self.nv = len(self.verts)
        self.facets = loadtxt(os.path.join(os.path.split(filename)[0], 
                                            "XFacetM.txt"), dtype=int) - 1
        self.nf = len(self.facets)
        self.calc_stretch()
        self.f_z = r_[[sum([self.verts[ind,2] for ind in face])/3
                        for face in self.facets]]
        self.calc_bend(filename)
        self.calc_area()
    
    def calc_stretch(self):
        """Calculate the stretching energy per facet, using the algorithm in 
        MEMstretchplot.m, from Eleni.  I hope it's correct."""
        
        nb12 = nb23 = nb13 = 0.1    # Default length of springs?
        
        ba12 = self.verts[self.facets[:,1],:] - self.verts[self.facets[:,0],:]
        ba23 = self.verts[self.facets[:,2],:] - self.verts[self.facets[:,1],:]
        ba13 = self.verts[self.facets[:,0],:] - self.verts[self.facets[:,2],:]
        nba12 = sqrt(ba12[:,0]**2 + ba12[:,1]**2 + ba12[:,2]**2)
        nba23 = sqrt(ba23[:,0]**2 + ba23[:,1]**2 + ba23[:,2]**2)
        nba13 = sqrt(ba13[:,0]**2 + ba13[:,1]**2 + ba13[:,2]**2)
        
        self.stretch = 1e8 * ((nba12-nb12)**2 + (nba23-nb23)**2 + (nba13-nb12)**2)/3
        # What is 1e8 doing at beginning?
        # MEMstretchplot contains some fiddling to the lowest energy facets, but
        # I'm guessing that's just to fix the display.

    def calc_bend(self, filename):
        """Calculate the bending energy per facet, as per MEMstretchplot.m"""
        
        #list12 = r_[self.facets[:,0], self.facets[:,1]]
        list3 = self.facets[:,2]
        #list23 = r_[self.facets[:,1], self.facets[:,2]]
        list1 = self.facets[:,0]
        #list31 = r_[self.facets[:,2], self.facets[:,0]]
        list2 = self.facets[:,1]
        
        AdjacentriM = loadtxt(os.path.join(os.path.split(filename)[0], 
                                            "XAdjacentriM.txt"), dtype=int) - 1
        
        facetlist = zeros((self.nf, 3), dtype=int) + len(AdjacentriM)
                
        for jf in range(self.nf):
            T1 = ((list1[jf] == AdjacentriM[:,0]) * (list2[jf] == AdjacentriM[:,1])) \
                    * (list3[jf] == AdjacentriM[:,2]) + \
                 ((list2[jf] == AdjacentriM[:,0]) * (list1[jf] == AdjacentriM[:,1])) \
                    * (list3[jf] == AdjacentriM[:,3])
            T2 = ((list2[jf] == AdjacentriM[:,0]) * (list3[jf] == AdjacentriM[:,1])) \
                    * (list1[jf] == AdjacentriM[:,2]) + \
                 ((list3[jf] == AdjacentriM[:,0]) * (list2[jf] == AdjacentriM[:,1])) \
                    * (list1[jf] == AdjacentriM[:,3])
            T3 = ((list3[jf] == AdjacentriM[:,0]) * (list1[jf] == AdjacentriM[:,1])) \
                    * (list2[jf] == AdjacentriM[:,2]) + \
                 ((list1[jf] == AdjacentriM[:,0]) * (list3[jf] == AdjacentriM[:,1])) \
                    * (list2[jf] == AdjacentriM[:,3])
            
            t1 = find(T1)
            t2 = find(T2)
            t3 = find(T3)
            if len(t1) > 1 or len(t2) > 1 or len(t3) > 1:
                print "Error near t1", t1, t2, t3
            
            if len(t1):
                facetlist[jf,0] = t1
            
            if len(t2):
                facetlist[jf,1] = t2
            
            if len(t3):
                facetlist[jf,2] = t3
            
        Costh0 = zeros(len(AdjacentriM))
        Sinth0 = zeros(len(AdjacentriM))
        Costh = zeros(len(AdjacentriM))
        Sinth = zeros(len(AdjacentriM))
        
        for ji in range(len(AdjacentriM)):
            n1,n2,n3,n4 = AdjacentriM[ji,:]
            av = self.verts[n1,:]
            bv = self.verts[n2,:]
            cv = self.verts[n3,:]
            cpv = self.verts[n4,:]
            
            ab = bv - av
            normab = norm(ab)
            ac = cv - av
            acp = cpv - av
            ccp = cpv - cv
            vec1 = cross(ab, ac)
            normv1 = norm(vec1)
            vec2 = cross(acp, ab)
            normv2 = norm(vec2)
            dot12 = dot(ab,ac)
            dot12 = dot(ab,acp)
            dot23 = dot(ac,acp)
            dot11 = dot(ab,ab)
            dot22 = dot(ac,ac)
            dot33 = dot(acp,acp)
            crossba = cross(bv, av)
            crosscpc = cross(cpv, cv)
            crossv1_v2_ab = dot(cross(vec1, vec2), ab)
            costh = dot(vec1, vec2) / (normv1*normv2)
            sinth = crossv1_v2_ab / (normv1*normv2*normab)
            
            Costh[ji] = costh
            Sinth[ji] = sinth
            
            Costh0[ji] = 1
            Sinth0[ji] = 0
        
        CosthA = r_[Costh, 0]
        Costh0A = r_[Costh0, 0]
        SinthA = r_[Sinth, 0]
        Sinth0A = r_[Sinth0, 0]
        
        self.f_bend = 1 - sum([CosthA[facetlist[:,i]] * Costh0A[facetlist[:,i]]
                               + SinthA[facetlist[:,i]] * Sinth0A[facetlist[:,i]]
                               for i in range(3)], 0)/3
