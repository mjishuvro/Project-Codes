import arcpy

arcpy.env.overwriteOutput = True

# Reading the Khal cross-section (XNS) and creating xns file feature layer
X_Section_Shape = r"E:\Script\Pycharm_Code\Khal_Embankment_Chainage\input\Kutubdia_Khal_XSection_for_HD_Model.shp"
arcpy.MakeFeatureLayer_management(X_Section_Shape, 'X_Section_points_shape_layer')

# Reading Khal Network shape file
Khal_Network_shp = r"E:\Script\Pycharm_Code\Khal_Embankment_Chainage\input\Kutubdia_Khal_Network_for_HD_Model.shp"

# Setting the output directory to write the output file
output_folder_dir = r'E:\Script\Pycharm_Code\Khal_Embankment_Chainage\output'

# Setting the khal and cross-section id field name of the shape file
XNS_Khal_field = 'HD_Khal'
Section_ID_field = 'HD_XNS_ID'

# Defining the spatial reference and file name of the chainage shape file
spatial_reference = r"E:\Script\Pycharm_Code\Khal_Embankment_Chainage\BTM_Everest_Bangladesh.prj"
ch_shp_file = r"E:\Script\Pycharm_Code\Khal_Embankment_Chainage\output\XNS_Chaiange"

# Defining the field name for the khal route shape file
Khal_alignment_route_id_field = 'Name'

# Defining an empty 'Khal_list' to store the khal name in the shape file
khal_list = []

# Defining an empty list to store the created individual khal network shape file name
shp_list = []


# Updating the khal list with unique khal name
with arcpy.da.UpdateCursor('X_Section_points_shape_layer', [XNS_Khal_field]) as u_cursor:
    for row in u_cursor:
        if row[0] not in khal_list:
            x = row[0].encode('ascii', 'ignore')
            khal_list.append(x)
# print(khal_list)


# Creating line for each cross-section from cross-sections points data for each khal
for khal in khal_list:
    arcpy.MakeFeatureLayer_management(X_Section_Shape, 'X_Section_points_shape_layer',
                                      """ "{}" = '{}' """.format(XNS_Khal_field, khal))

    output_Cross_Section_Line = r"{}\{}_Line.shp".format(output_folder_dir, khal)

    Line_Field = Section_ID_field

    arcpy.PointsToLine_management('X_Section_points_shape_layer', output_Cross_Section_Line, Line_Field)

    arcpy.MakeFeatureLayer_management(output_Cross_Section_Line, 'XNS_Line_layer')

# Adding khal remarks field
    # Adding a field to give remarks of khal name for each cross-section
    field = XNS_Khal_field
    arcpy.AddField_management(output_Cross_Section_Line, field, 'TEXT')

    # Updating khal remarks field
    with arcpy.da.UpdateCursor(output_Cross_Section_Line, [XNS_Khal_field]) as u_cursor:
        for row in u_cursor:
            row[0] = khal
            u_cursor.updateRow(row)

    # Appending the khal shape file list
    shp_list.append(output_Cross_Section_Line)

# Merging all the individual khal cross-section line shape to create a combined shape file
merged_shape_XNS_line = r"{}\Merged_Cross_Section_Line.shp".format(output_folder_dir)
arcpy.Merge_management(shp_list, merged_shape_XNS_line)

# Deleting the individual khal cross-section line shape
for shp_file in shp_list:

    if arcpy.Exists(shp_file) and arcpy.TestSchemaLock(shp_file):
        arcpy.Delete_management(shp_file)

    else:
        print("Cannot delete {}.".format(shp_file))
        print("The file either doesn't exist or is locked by another application.")


# Getting the intersecting points of khal line and cross-section line shape file
Cross_Section_Line = merged_shape_XNS_line
arcpy.MakeFeatureLayer_management(Cross_Section_Line, 'Cross_Section_Line_Layer')

Khal_alignment_CL = Khal_Network_shp
arcpy.MakeFeatureLayer_management(Khal_alignment_CL, 'Center_Line_Layer')

intersecting_lines_layer = ['Center_Line_Layer', 'Cross_Section_Line_Layer']
intersecting_points_shp = r"{}\Khal_Network_CL_and_XNS_intersecting_points.shp".format(output_folder_dir)

arcpy.Intersect_analysis(intersecting_lines_layer, intersecting_points_shp, output_type='POINT')


# Adding XY Coordinate Field to the Intersecting Points shape file
points_shp_in_feature = intersecting_points_shp
arcpy.MakeFeatureLayer_management(points_shp_in_feature, 'point_shp_for_xy_field')

arcpy.AddXY_management('point_shp_for_xy_field')


# Creating Route Shape File
Khal_alignment_CL = Khal_Network_shp
arcpy.MakeFeatureLayer_management(Khal_alignment_CL, 'Center_Line_Layer')

route_id_field = Khal_alignment_route_id_field
out_route_shape = r"{}\Khal_Network_CL_Route.shp".format(output_folder_dir)

arcpy.CreateRoutes_lr(Khal_alignment_CL, route_id_field, out_route_shape)


# Locating Feature Points along Routes
points_shp_chainage = intersecting_points_shp
arcpy.MakeFeatureLayer_management(points_shp_in_feature, 'point_shp_for_locating_chainage')

route_shape = out_route_shape

out_table = r"{}\located_points.dbf".format(output_folder_dir)
props = 'Remarks POINT Chainage'  # Route_Identifier_Field, Event Type(POINT or LINE), Give a Name of the Measured Field

arcpy.LocateFeaturesAlongRoutes_lr(points_shp_chainage, route_shape, route_id_field, radius_or_tolerance=0.2,
                                   out_table=out_table, out_event_properties=props)


# Creating shape file from the chainage table
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
