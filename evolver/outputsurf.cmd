// outputsurf.cmd

// Output the surface - the vertices and facets, their energies, and
// the un-strained configuration

outputsurf := {
	printf "# Surface output: vertices, faces\n"; 
	printf "%g %g 0 0 0 0 0\n",count(vertices ,1), count(facets ,1); 
	printf "# Vertices: coords, bend, ref_coords\n"; 
	foreach vertices do 
		printf "%g %g %g %g %g %g %g\n",
			x, y, z, bend,  ref_coord[1],  ref_coord[2],  ref_coord[3]; 
	printf "# Faces: vertices, stretch, form factors\n"; 
	foreach facets ff do 
		printf "%g %g %g %g %g %g %g\n",
			ff.vertex[1].id, ff.vertex[2].id, ff.vertex[3].id, stretch,
			form_factors[1],  form_factors[2],  form_factors[3]
}
