import arcpy
import os

arcpy.env.overwriteOutput = True

# Setting file path of embankment cross-section points shape file path
# and splitting the file path to create the file path list
cross_section_points = r"E:\Script\Pycharm_Code\Embankment_Chainage\Input\Embankment_Cross_Section.shp"
xns_point_path_list = cross_section_points.split(os.sep)

# Setting the field name of the shape cross-section point shape file to create the cross-section line (USER INPUT)
Line_Field = 'Section_ID'

# Setting the output folder path (USER INPUT)
output_path = r"E:\Script\Pycharm_Code\Embankment_Chainage\Output"

# Setting file path of the embankment center line shape file and making feature layer (USER INPUT)
# and splitting the file path to create the file path list
center_line = r"E:\Script\Pycharm_Code\Embankment_Chainage\Input\Embankment_Alignment.shp"
center_line_path_list = center_line.split(os.sep)
arcpy.MakeFeatureLayer_management(center_line, 'Center_Line_Layer')

# Setting the spatial reference of the chainage points shape file (USER INPUT)
spatial_reference = r"E:\Script\Pycharm_Code\Embankment_Chainage\BTM_Everest_Bangladesh.prj"

# Defining the output file name of the chainage shape file
ch_shp_file = os.path.join(output_path, "{}_chainage".format(xns_point_path_list[-1][:-4]))


# CROSS-SECTION POINTS TO LINE CONVERSION

# Defining the name of points line shape file and converting cross-section points to line shape file
output_Cross_Section_Line = os.path.join(output_path, "{}_Line.shp".format(xns_point_path_list[-1][:-4]))
arcpy.PointsToLine_management(cross_section_points, output_Cross_Section_Line, Line_Field)


# CROSS-SECTION LINE AND EMBANKMENT ALIGNMENT INTERSECTING POINTS

# Creating feature layer from cross-section line shape file
cross_section_line = output_Cross_Section_Line
arcpy.MakeFeatureLayer_management(cross_section_line, 'Cross_Section_Line_Layer')

# Specifying the intersecting layers name
intersecting_lines_layer = ['Center_Line_Layer', 'Cross_Section_Line_Layer']

# Defining the output intersecting points shape file and creating the intersecting points
output_points_shape = os.path.join(output_path, 'intersecting_points.shp')
arcpy.Intersect_analysis(intersecting_lines_layer, output_points_shape, output_type='POINT')


# ADDING XY CO-ORDINATE FIELD TO THE INTERSECTING POINTS SHAPE FILE

# Setting the intersecting points shape file and making feature layer of it
points_shp_in_feature = output_points_shape
arcpy.MakeFeatureLayer_management(points_shp_in_feature, 'point_shp_for_xy_field')

# Adding the xy co-ordinate to the intersecting points feature layer
arcpy.AddXY_management('point_shp_for_xy_field')


# CREATING THE ROUTE SHAPE FILE FROM EMBANKMENT ALIGNMENT SHAPE FILE

# Defining the route id field name
route_id_field = 'Remarks'

# Defining the route shape file name and creating the route shape file
out_route_shape = os.path.join(output_path, "{}_route.shp".format(center_line_path_list[-1][:-4]))
arcpy.CreateRoutes_lr(center_line, route_id_field, out_route_shape)


# LOCATING THE POINTS FEATURES ALONG THE ROUTE

# Specifying the points feature shape file and creating points feature of it
points_shape = output_points_shape
arcpy.arcpy.MakeFeatureLayer_management(points_shape, 'Points_shape_layer')

# Setting the route the shape file
route_shape = out_route_shape

# Setting the output table name
out_table = os.path.join(output_path, "located_points.dbf")

# Setting the Route_Identifier_Field, Event Type(POINT or LINE), Giving a Name for the Measured Field
props = 'Remarks POINT Chainage'

arcpy.LocateFeaturesAlongRoutes_lr(points_shape, route_shape, route_id_field, radius_or_tolerance=0.2,
                                   out_table=out_table, out_event_properties=props)


# CREATING SHAPE FILE FROM THE TABLE

# Defining the spatial reference
co_ordinate_system = spatial_reference

# Setting the local variables
in_table = out_table
x_coordinate = "POINT_X"
y_coordinate = "POINT_Y"
out_layer = "Chainage_Points"

# Making the XY Event layer
arcpy.MakeXYEventLayer_management(in_table, x_coordinate, y_coordinate, out_layer, co_ordinate_system)

# Shape file output shape file name and path and crea
shp_file = ch_shp_file
arcpy.CopyFeatures_management(out_layer, shp_file)

# Removing the created layer (necessary while iterating)
del out_layer

# Deleting the created table
arcpy.Delete_management(in_table)
