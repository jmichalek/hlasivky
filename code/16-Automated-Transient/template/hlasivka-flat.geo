DefineConstant [
  showLines = {Geometry.Lines, Choices {0,1}, Name "Options/Show lines",
              GmshOption "Geometry.Lines", AutoCheck 0}
  showPoints = {Geometry.Points, Choices {0,1}, Name "Options/Show points",
               GmshOption "Geometry.Points", AutoCheck 0}
  showNodes = {Mesh.Points, Choices {0,1}, Name "Options/Show nodes",
                GmshOption "Mesh.Points", AutoCheck 0}

  recombineAll = { 1 , Choices {0,1}, Name "Meshing/Recombine",
                GmshOption "Mesh.RecombineAll", AutoCheck 1}
  lcExt = {4., Name "Meshing/Exterior"}
  blayer_thickness = {0.22, Name "Meshing/Blayer/Thickness"}
  blayer_ratio = {2.25, Name "Meshing/Blayer/Ratio"}
  blayer_hwall_n = {0.06, Name "Meshing/Blayer/hwall_n"}
  blayer_hwall_t = {0.12, Name "Meshing/Blayer/hwall_t"}
  central_h = {TMPCENTRALH, Name "Meshing/Blayer/central_h"}
  smoothing = {1 , Name "Meshing/Smoothing"}
];

hdist = TMPHDIST;
vertshift = 0.3 - hdist;
cl__1 = 1;
Point(1) = {0, 0, 0, 1};
Point(4) = {5, 0, 0, 1};
Point(5) = {1.3, 0, 0, 1};
Point(6) = {1.2, 0.2, 0, 1};
Point(7) = {1.2, 0.5, 0, 1};
Point(8) = {0.7, 0.3, 0, 1};
Point(9) = {0.2, 0, 0, 1};
Point(10) = {1.264, -0.2, 0, 1};
Point(11) = {0.2, -0.2, 0, 1};
Point(12) = {3, 0, 0, 1};
Point(13) = {2, 0.1, 0, 1};
Point(14) = {1.5, 0.4, 0, 1};
Point(15) = {1.5, 0.1, 0, 1};
Point(16) = {1.4, 0, 0, 1};
Point(17) = {1.35, 0.3, 0, 1};
Point(18) = {0.2, -0.03, 0, 1};
Point(19) = {1.264, 0, 0, 1};
Point(20) = {1.172, 0.184, 0, 1};
Point(21) = {1.172, 0.47, 0, 1};
Point(22) = {0.712, 0.276, 0, 1};
Point(23) = {0.252, 0, 0, 1};
Point(25) = {1.04, 0.37, -0, 1};
Point(26) = {0.89, 0.3, -0, 1};
Point(27) = {0.96, 0.19, -0, 1};
Point(28) = {1.1, 0.29, -0, 1};
Point(29) = {1.04, 0.93, 0, 1};
Point(30) = {0.89, 1, 0, 1};
Point(31) = {0.96, 1.11, 0, 1};
Point(32) = {1.1, 1.01, 0, 1};
Point(43) = {1.264, 1.3, 0, 1};
Point(44) = {1.264, 1.5, 0, 1};
Point(48) = {0.2, 1.5, 0, 1};
Point(52) = {0.2, 1.33, 0, 1};
Point(56) = {0.252, 1.3, 0, 1};
Point(60) = {0.712, 1.024, 0, 1};
Point(61) = {1.172, 0.83, 0, 1};
Point(62) = {1.172, 1.116, 0, 1};
Point(66) = {1.3, 1.3, 0, 1};
Point(67) = {1.2, 1.1, 0, 1};
Point(68) = {1.2, 0.8, 0, 1};
Point(69) = {0.7, 1, 0, 1};
Point(70) = {0.2, 1.3, 0, 1};
Point(71) = {5, 1.3, 0, 1};
Point(72) = {3, 1.3, 0, 1};
Point(76) = {0, 1.3, 0, 1};
Point(80) = {2, 1.2, 0, 1};
Point(81) = {1.5, 0.9, 0, 1};
Point(82) = {1.35, 1, 0, 1};
Point(83) = {1.5, 1.2, 0, 1};
Point(84) = {1.4, 1.3, 0, 1};




Line(4) = {4, 12};
Spline(5) = {5, 6, 7, 8, 9};
Line(6) = {9, 1};
Line(7) = {19, 10};
Line(8) = {10, 11};
Line(9) = {11, 18};
Spline(11) = {12, 13, 14, 17, 15, 16, 5};
Spline(12) = {19, 20, 21, 22, 23};

Line(13) = {18, 9};

Line(14) = {23, 18};

Spline(15) = {25, 26, 27, 28, 25};
Line(18) = {19, 5};
Spline(26) = {29, 30, 31, 32, 29};
Line(29) = {43, 44};
Line(30) = {44, 48};
Line(31) = {48, 52};
Line(32) = {52, 56};
Spline(33) = {56, 60, 61, 62, 43};
Spline(35) = {66, 67, 68, 69, 70};
Line(36) = {70, 52};
Line(39) = {43, 66};
Line(40) = {71, 72};
Line(41) = {70, 76};
Spline(42) = {72, 80, 81, 82, 83, 84, 66};
Line(43) = {76, 1};
Line(44) = {71, 4};
Line Loop(20) = {15};
Plane Surface(20) = {20}; // dolní sval

Line Loop(24) = {5, -13, -14, -12, 18};
Plane Surface(24) = {24}; // dolní vrstva

Line Loop(25) = {26};
Plane Surface(25) = {25}; // horní sval

Line Loop(34) = {35, 36, 32, 33, 39};
Plane Surface(34) = {34}; // horní vrstva
Line Loop(46) = {43, -6, -5, -11, -4, -44, 40, 42, 35, 41};
Plane Surface(46) = {46}; // trubice



Translate {0, - vertshift, 0} {
  Point{76, 48, 52, 70, 56, 60, 69, 44, 31, 30, 43, 66, 62, 32, 67, 84, 29, 83, 61, 82, 68, 81, 80, 72, 71};
}
Translate {TMPCHANNELLENGTH, 0, 0} {
  Point{71,4};
}

Translate {-TMPCHANNELSTART, 0, 0} {
  Point{76,1};
}


Line Loop(47) = {29, 30, 31, 32, 33};
Plane Surface(48) = {25, 47}; // horní hlasivka
Line Loop(49) = {12, 14, -9, -8, -7};
Plane Surface(50) = {20, 49}; // dolní hlasivka

Mesh.CharacteristicLengthExtendFromBoundary = 1;



// Meshing options
Mesh.ElementOrder = 1;
Mesh.Algorithm = TMPMESHALGO; // (0) Automatic (1) MeshAdapt (5) Delauney (6) Frontal (8) Delauney Quad (9) Packing of parallelograms
Mesh.RemeshAlgorithm = 1; // (0) no split (1) automatic (2) automatic only with metis
Mesh.RemeshParametrization = 0; // (0) harmonic (1) conformal spectral (7) conformal finite element
Mesh.RecombinationAlgorithm = 0;  // (0) standard (1) blossom
Mesh.SubdivisionAlgorithm = 1; // (0) None (1) All Quads (2) All Hexas
Mesh.RecombineAll=recombineAll;
Mesh.Smoothing = smoothing;


Field[1] = BoundaryLayer;
Field[1].EdgesList = {5, 13, 14, 12, 18};
//Field[1].NodesList = {9, 8, 7, 6, 5, 19, 20, 21, 22, 23, 18};
FanNodesList = {21};
Field[1].hfar = lcExt;
Field[1].hwall_n = blayer_hwall_n;
Field[1].hwall_t = blayer_hwall_t;
Field[1].thickness = blayer_thickness;
Field[1].ratio = blayer_ratio;
Field[1].Quads = 1;
BoundaryLayer Field = 1;

Field[2] = BoundaryLayer;
Field[2].EdgesList = {35, 36, 32, 33, 39};
//Field[2].NodesList = {52, 60, 61, 62, 43, 66, 67, 68, 69, 70};
FanNodesList = {61};
Field[2].hfar = lcExt;
Field[2].hwall_n = blayer_hwall_n;
Field[2].hwall_t = blayer_hwall_t;
Field[2].thickness = blayer_thickness;
Field[2].ratio = blayer_ratio;
Field[2].Quads = 1;
BoundaryLayer Field = 2;

Field[4] = Box;
Field[4].VIn = central_h;
Field[4].VOut = lcExt;

Field[4].XMin = 0.7;
Field[4].XMax = 1.8;
Field[4].YMin = 0.3;
Field[4].YMax = 0.7 + hdist;

Field[3] = Min;
Field[3].FieldsList = {1, 2,4};
Background Field = 3;

Mesh.CharacteristicLengthMax = TMPGLOBALLC;

Mesh 2;
TMPREFINE
//OptimizeMesh Gmsh;
Mesh.Format = 1;
Save "hlasivka.msh";
//Print "file.png";
Exit;
