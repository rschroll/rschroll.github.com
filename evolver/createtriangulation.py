#! /usr/bin/env python

def createTriangulation(n):
    """Create a base triangulation with length n*width"""
    
    v = "vertices\n"
    e = "edges\n"
    f = "faces\n"
    
    # Beginning section
    v += "1  0 boundary 1 fixed ref_coord {0 0 0}\n" + \
         "2  xm boundary 1 fixed ref_coord {1 0 0}\n"
    e += "1  1 2 boundary 1\n" + \
         "2  1 3\n" + \
         "3  2 3\n" + \
         "4  1 4 fixed\n" + \
         "5  2 5 fixed\n"
         # missing 6
    f += "1  1  3 -2\n" + \
         "2  4 -7 -2\n" + \
         "3  5 -9 -3\n"
    
    # n-1 middle sections
    for a in range(1,n):
        v += "%i  xm/2 %f mh ref_coord {0.5 %f 0}\n"%(3*a, a-0.5, a-0.5) + \
             "%i  0 %i 0 fixed ref_coord {0 %f 0}\n"%(3*a+1, a, a) + \
             "%i  xm %i 0 fixed ref_coord {1 %f 0}\n"%(3*a+2, a, a)
        e += "%i  %i %i\n"%(7*a,   3*a, 3*a+1) + \
             "%i  %i %i\n"%(7*a+1, 3*a, 3*a+3) + \
             "%i  %i %i\n"%(7*a+2, 3*a, 3*a+2) + \
             "%i  %i %i\n"%(7*a+3, 3*a+1, 3*a+3) + \
             "%i  %i %i\n"%(7*a+4, 3*a+2, 3*a+3) + \
             "%i  %i %i fixed\n"%(7*a+5, 3*a+1, 3*a+4) + \
             "%i  %i %i fixed\n"%(7*a+6, 3*a+2, 3*a+5)
        f += "%i  %i  %i -%i\n"%(4*a,   7*a,   7*a+3, 7*a+1) +\
             "%i  %i  %i -%i\n"%(4*a+1, 7*a+2, 7*a+4, 7*a+1) +\
             "%i  %i -%i -%i\n"%(4*a+2, 7*a+5, 7*a+7, 7*a+3) +\
             "%i  %i -%i -%i\n"%(4*a+3, 7*a+6, 7*a+9, 7*a+4)
    
    # End section
    a = n
    v += "%i  xm/2 %f mh ref_coord {0.5 %f 0}\n"%(3*a, a-0.5, a-0.5) + \
         "%i  0 %i 0 fixed ref_coord {0 %f 0}\n"%(3*a+1, a, a) + \
         "%i  xm %i 0 fixed ref_coord {1 %f 0}\n"%(3*a+2, a, a)
    e += "%i  %i %i\n"%(7*a,   3*a, 3*a+1) + \
         "%i  %i %i\n"%(7*a+1, 3*a+1, 3*a+2) + \
         "%i  %i %i\n"%(7*a+2, 3*a, 3*a+2)
    f += "%i  %i  %i -%i\n"%(4*a, 7*a, 7*a+1, 7*a+2)
    
    return "\n".join((v,e,f))

def main(n):
    """Write out the .fe file."""
    print """// File created by createtriangulation.py
// Length = %i * Width

PARAMETER Ak = 2*pi*0.2 // Amplitude * wavenumber
PARAMETER kk = 6 * sqrt(Ak^2 + 1) * EllipticE(1/(1+Ak^-2))
PARAMETER Ampl = Ak/kk
PARAMETER xm = 3*pi/kk

PARAMETER mh = 0

// For resetting form_factors in refining
define vertex attribute ref_coord real[3]
define vertex attribute old_vid  integer
define edge   attribute old_eid  integer

define facet attribute poisson_ratio real
define facet attribute form_factors real[3]
quantity stretch energy method linear_elastic global
quantity bend energy modulus 0.0001 method star_perp_sq_mean_curvature global

boundary 1 parameters 1
	x1: p1
	x2: 0
	x3: Ampl * sin(kk*p1)
""" % n
    print createTriangulation(n)
    print """read

set facet poisson_ratio 0.25
set facet tension 0

// Set form factors so initial cube is unstretched.
set_form_factors := {
foreach facet ff do 
{ set ff.form_factors[1]  
          (ff.vertex[2].ref_coord[1] - ff.vertex[1].ref_coord[1])^2
        + (ff.vertex[2].ref_coord[2] - ff.vertex[1].ref_coord[2])^2
        + (ff.vertex[2].ref_coord[3] - ff.vertex[1].ref_coord[3])^2;
  set ff.form_factors[2]  
          (ff.vertex[2].ref_coord[1] - ff.vertex[1].ref_coord[1])
         *(ff.vertex[3].ref_coord[1] - ff.vertex[1].ref_coord[1])
        + (ff.vertex[2].ref_coord[2] - ff.vertex[1].ref_coord[2])
         *(ff.vertex[3].ref_coord[2] - ff.vertex[1].ref_coord[2])
        + (ff.vertex[2].ref_coord[3] - ff.vertex[1].ref_coord[3])
         *(ff.vertex[3].ref_coord[3] - ff.vertex[1].ref_coord[3]);
  set ff.form_factors[3]  
          (ff.vertex[3].ref_coord[1] - ff.vertex[1].ref_coord[1])^2
        + (ff.vertex[3].ref_coord[2] - ff.vertex[1].ref_coord[2])^2
        + (ff.vertex[3].ref_coord[3] - ff.vertex[1].ref_coord[3])^2;
}
}
set_form_factors;

// redefine the "r" command to adjust form factors.
r :::= { 
     set vertex old_vid id;
     set edge old_eid id;
     'r'; 
     foreach vertex vv where old_vid == 0 do
     { vv.ref_coord[1] := 
          avg(vv.edge ee where old_eid != 0,sum(ee.vertex where old_vid != 0,
                    ref_coord[1]));
       vv.ref_coord[2] := 
          avg(vv.edge ee where old_eid != 0,sum(ee.vertex where old_vid != 0,
                    ref_coord[2]));
       vv.ref_coord[3] := 
          avg(vv.edge ee where old_eid != 0,sum(ee.vertex where old_vid != 0,
                    ref_coord[3]));
     };
     set_form_factors;
     recalc;
}"""
    
if __name__ == "__main__":
    import sys
    try:
        arg = int(sys.argv[1])
    except (TypeError, IndexError):
        sys.stderr.write("Must past aspect ratio as argument.\n")
        sys.exit(1)
    main(arg)
