import arcpy
import os
import glob

arcpy.env.overwriteOutput = True

# Setting the East, West, North and South boundary line of the study area
# and creating individual feature line layer
East_line = r"E:\Script\Salinity_Impacted_Area\Input_Data\Boundary_Polyline\East_Polyline.shp"
arcpy.MakeFeatureLayer_management(East_line, 'East_line')

West_line = r"E:\Script\Salinity_Impacted_Area\Input_Data\Boundary_Polyline\West_Polyline.shp"
arcpy.MakeFeatureLayer_management(West_line, 'West_line')

North_line = r"E:\Script\Salinity_Impacted_Area\Input_Data\Boundary_Polyline\North_PolyLine.shp"
arcpy.MakeFeatureLayer_management(North_line, 'North_line')

South_line = r"E:\Script\Salinity_Impacted_Area\Input_Data\Boundary_Polyline\South_Polyline.shp"
arcpy.MakeFeatureLayer_management(South_line, 'South_line')

output = r'E:\Script\Salinity_Impacted_Area\Input_Data\Selection_Area'
Clipped_area = r'E:\Script\Salinity_Impacted_Area\Input_Data\Clipped_Area'

# Setting interested salinity class layer
layer_list = [[1], [1, 2], [2, 4], [4, 5], [5, 10], [10, 15], [15, 20], [20, 25], [25]]

# Setting the salinity contour line file path
contour_shape = r"E:\Script\Salinity_Impacted_Area\Input_Data\Baseline_2019_Contour\April_Edited.shp"

# Iterating through each class of the class layer list and
# extracting the contour polygon and creating the polygon for selecting the clipped area
for x in layer_list:

    if len(x) == 1:
        arcpy.MakeFeatureLayer_management(contour_shape, 'contour_layer', """ "Contour" = {} """.format(x[0]))

        if x[0] == layer_list[0][0]:

            in_features = ['East_line', 'West_line', 'North_line', 'contour_layer']

            output_file_name = '0_{}_ppt.shp'.format(x[0])  # type: str
            out_file = os.path.join(output, output_file_name)

            arcpy.FeatureToPolygon_management(in_features, out_file)

        elif x[0] == layer_list[-1][0]:
            arcpy.MakeFeatureLayer_management(contour_shape, 'contour_layer', """ "Contour" = {} """.format(x[0]))

            in_features = ['East_line', 'West_line', 'South_line', 'contour_layer']

            output_file_name = 'more_than_{}_ppt.shp'.format(x[0])
            out_file = os.path.join(output, output_file_name)

            arcpy.FeatureToPolygon_management(in_features, out_file)

        else:
            pass

    elif len(x) == 2:

        arcpy.MakeFeatureLayer_management(contour_shape, 'contour_layer1', """ "Contour" = {} """.format(x[0]))
        arcpy.MakeFeatureLayer_management(contour_shape, 'contour_layer2', """ "Contour" = {} """.format(x[1]))

        in_features = ['East_line', 'West_line', 'contour_layer1', 'contour_layer2']

        output_file_name = '{}_{}_ppt.shp'.format(x[0], x[1])
        out_file = os.path.join(output, output_file_name)

        arcpy.FeatureToPolygon_management(in_features, out_file)

    else:
        pass

    print(x)

# Setting district area shape file path and creating the feature layer of it
district_area_shp = r"E:\Script\Salinity_Impacted_Area\Input_Data\Area_with_districts\Baseline_2019_Edited_April.shp"
arcpy.MakeFeatureLayer_management(district_area_shp, 'district_area_layer')

# Defining an empty list to store the clipped salinity
# impacted area shape file for each class
salinity_impacted_area_class_list = []

# Iterating through each file selecting the clipped area and updating contour area
# class in the slitted district area shape file
for sel_area_file in glob.glob(r'E:\Script\Salinity_Impacted_Area\Input_Data\Selection_Area\*.shp'):

    file_path_list = os.path.split(sel_area_file)
    name2 = (file_path_list[-1].split('.shp'))
    name = name2[0]

    arcpy.MakeFeatureLayer_management(sel_area_file, 'ppt_area_layer')

    field = 'Remarks'
    arcpy.AddField_management('ppt_area_layer', field, 'TEXT')

    output_file_name = '{}_Area.shp'.format(name)
    Area_out_file = os.path.join(Clipped_area, output_file_name)

    arcpy.Clip_analysis('district_area_layer', 'ppt_area_layer', Area_out_file)

    arcpy.MakeFeatureLayer_management(Area_out_file, 'Clipped_area_layer')
    in_shape = arcpy.AddField_management('Clipped_area_layer', field, 'TEXT')

    with arcpy.da.UpdateCursor(in_shape, ['Remarks']) as u_cursor:
        for row in u_cursor:
            row[0] = name
            u_cursor.updateRow(row)
    print(output_file_name)

    salinity_impacted_area_class_list.append(Area_out_file)


# CREATING A SINGLE SHAPE FILE BY MERGING ALL THE CLIPPED AREA SHAPE FILE

# Merging all the clipped salinity area shape file
impacted_dist_area_shp = r"E:\Script\Salinity_Impacted_Area\Output\Baseline_2019_Area_Impacted_Merged.shp"
arcpy.Merge_management(salinity_impacted_area_class_list, impacted_dist_area_shp)


# CALCULATING THE SHAPE AREA FIELD IN SQUARE KILOMETERS

# Adding field of type 'DOUBLE' to calculate the area
area_field = 'Area_sqkm'
field_type = 'DOUBLE'

arcpy.MakeFeatureLayer_management(impacted_dist_area_shp, 'Impacted_district_Area_layer')
arcpy.AddField_management('Impacted_district_Area_layer', area_field, field_type)

# Calculating the area in square kilometers
arcpy.CalculateField_management('Impacted_district_Area_layer', area_field,
                                "!SHAPE.area@SQUAREKILOMETERS!",
                                "PYTHON")
