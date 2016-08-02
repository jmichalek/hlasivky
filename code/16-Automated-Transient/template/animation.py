try: paraview.simple
except: from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

import glob
pattern = 'case*.vtu'
files = sorted(glob.glob(pattern))

case00 = XMLUnstructuredGridReader( FileName=files )

AnimationScene1 = GetAnimationScene()

case00.PointArrayStatus = ['pressure', 'displacement', 'velocity', 'mesh velocity']
case00.CellArrayStatus = ['GeometryIds']

AnimationScene1.PlayMode = 'Snap To TimeSteps'

RenderView1 = GetRenderView()
DataRepresentation1 = Show()
DataRepresentation1.EdgeColor = [0.0, 0.0, 0.5000076295109483]
DataRepresentation1.SelectionPointFieldDataArrayName = 'displacement'
DataRepresentation1.SelectionCellFieldDataArrayName = 'GeometryIds'
DataRepresentation1.ScalarOpacityUnitDistance = 0.0030380135466787587
DataRepresentation1.ScaleFactor = 0.005000000000000001

RenderView1.CameraFocalPoint = [0.025, 0.005999999999999999, 0.0]
RenderView1.CameraPosition = [0.025, 0.005999999999999999, 10000.0]
RenderView1.InteractionMode = '2D'
RenderView1.CenterOfRotation = [0.025, 0.005999999999999999, 0.0]

a3_velocity_PVLookupTable = GetLookupTableForArray( "velocity", 3, RGBPoints=[0.0, 0.23, 0.299, 0.754, 10.916784177720363, 0.706, 0.016, 0.15], VectorMode='Magnitude', NanColor=[0.25, 0.0, 0.0], ColorSpace='Diverging', ScalarRangeInitialized=1.0, AllowDuplicateScalars=1 )

a3_velocity_PiecewiseFunction = CreatePiecewiseFunction( Points=[0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0] )

RenderView1.CameraPosition = [0.025, 0.005999999999999999, 0.10141761200925523]
RenderView1.CameraClippingRange = [0.10040343588916267, 0.10293887618939405]
RenderView1.CameraParallelScale = 0.026248809496813377

DataRepresentation1.ScalarOpacityFunction = a3_velocity_PiecewiseFunction
DataRepresentation1.ColorArrayName = ('POINT_DATA', 'velocity')
DataRepresentation1.LookupTable = a3_velocity_PVLookupTable

a3_velocity_PVLookupTable.ScalarOpacityFunction = a3_velocity_PiecewiseFunction

WriteAnimation('video.ogv', Magnification=1, Quality=2, FrameRate=15.000000)


Render()

