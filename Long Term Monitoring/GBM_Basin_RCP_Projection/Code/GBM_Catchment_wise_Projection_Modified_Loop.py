import arcpy
import pandas as pd
import os
import glob

arcpy.env.overwriteOutput = True


def blank_basin_projection(gridded_points_shp_path, catchment_area_shp_path, output_path):
    # Setting the path of gridded points data shape file
    gridded_points_shp = gridded_points_shp_path
    arcpy.MakeFeatureLayer_management(gridded_points_shp, 'Gridded_Points_layer')
    gridded_points_path_list = gridded_points_shp.split(os.sep)

    # Setting the output folder path
    output_path = output_path

    # Setting the path of the catchment area polygon feature
    catchment_area_shp = catchment_area_shp_path
    arcpy.MakeFeatureLayer_management(catchment_area_shp, 'catchment_area_layer')
    catchment_area_shp_path_list = catchment_area_shp.split(os.sep)

    # CREATING THIESSEN POLYGON

    # Setting the output thiessen polygon shape file name
    # and fields to be included from the points shape file
    thiessen_polygon_feature = os.path.join(output_path,
                                            '{}_thiessen_polygon.shp'.format(gridded_points_path_list[-1][:-4]))

    if arcpy.Exists(thiessen_polygon_feature):
        pass

    else:
        out_fields = "ALL"
        arcpy.CreateThiessenPolygons_analysis('Gridded_Points_layer', thiessen_polygon_feature, out_fields)

    # CLIPPING THE FEATURE

    # Setting the thiessen polygon feature shape file and making feature layer of it
    thieseen_polygon_shp = thiessen_polygon_feature
    arcpy.MakeFeatureLayer_management(thieseen_polygon_shp, 'Thiessen_Polygon_layer')

    # Defining the name of the clip area polygon
    clipped_thiesen_polygon_shp = os.path.join(output_path,
                                               "{}_Weightage.shp".format(catchment_area_shp_path_list[-1][:-4]))
    xy_tolerance = ""

    # Executing the Clip
    arcpy.Clip_analysis('Thiessen_Polygon_layer', 'catchment_area_layer', clipped_thiesen_polygon_shp, xy_tolerance)

    # ADDING AREA AND WEIGHTAGE COLUMN

    # Adding field in the clipped area
    arcpy.MakeFeatureLayer_management(clipped_thiesen_polygon_shp, 'clipped_Area_layer')

    # Creating a list with name of the field to be added in the clipped shape file
    area_weightage_field = ['Area_sqkm', 'Weightage', 'Remarks']
    data_type = ['DOUBLE', 'DOUBLE', 'TEXT']

    # Iterating through the list and adding the fields in the shape file (field type: DOUBLE)
    for field_name, field_type in zip(area_weightage_field, data_type):
        arcpy.AddField_management('clipped_Area_layer', field_name, field_type)

    # CALCULATING THE SHAPE AREA FIELD IN SQUARE KILOMETERS
    arcpy.CalculateField_management('clipped_Area_layer', area_weightage_field[0],
                                    "!SHAPE.area@SQUAREKILOMETERS!",
                                    "PYTHON")

    # CALCULATING TOTAL AREA OF THE CATCHMENT

    # Defining an empty list to store the area of each segment in the catchment
    segment_area_list = []

    # Iterating through the area field and updating the segment area list
    with arcpy.da.UpdateCursor('clipped_Area_layer', area_weightage_field[0]) as cursor:
        for area in cursor:
            segment_area_list.append(area[0])

    # Calculating the total area of the catchment from the segment area list
    catchment_area = sum(segment_area_list)

    # CALCULATING THE WEIGHTAGE OF EACH SEGMENT OF THE CATCHMENT AND UPDATING IT INTO THE WEIGHTAGE FIELD
    with arcpy.da.UpdateCursor('clipped_Area_layer', area_weightage_field) as cursor:
        for segment_row in cursor:
            weightage = segment_row[0] / catchment_area
            segment_row[1] = weightage
            segment_row[2] = catchment_area_shp_path_list[-1][:-4]
            cursor.updateRow(segment_row)

    return clipped_thiesen_polygon_shp


# Setting file path of GBM catchment shape file
basin_boundary = r"E:\Script\GBM_Basin_RCP_Projection\Input_Data\Basin_Boundary\GBM_WGS84.shp"

# Setting the output folder path
out_folder = r"E:\Script\GBM_Basin_RCP_Projection\Output\Basin_Wise_Projection"

# Reading the GBM Basin catchment list file
c_df = pd.read_csv(r"E:\Script\GBM_Basin_RCP_Projection\Input_Data\GBM_Basin_Catchment_List.csv")

for point_shp_file in glob.glob(r"E:\Script\GBM_Basin_RCP_Projection\Output\Gridded_data_shape\*.shp"):

    # Splitting the point shape file path to create a path list
    point_shp_path_list = point_shp_file.split(os.sep)

    # Creating a new folder to store the shape file
    if os.path.exists(os.path.join(out_folder, "{}".format(point_shp_path_list[-1][:-4]))):
        pass

    else:
        os.mkdir(os.path.join(out_folder, "{}".format(point_shp_path_list[-1][:-4])))

    # Setting the output folder path
    out_path = os.path.join(out_folder, "{}".format(point_shp_path_list[-1][:-4]))

    # Setting folder path of gridded points shape file
    points_shp = point_shp_file

    # Creating a points feature layer from points shape file
    arcpy.MakeFeatureLayer_management(points_shp, 'points_layer')

    # Creating a list to store the created shape file
    with_points_shp_path_list = []
    without_points_shp_path_list = []

    for catchment in c_df['Catchment_ID']:

        # Creating feature layer from shape file to use as input file in selection by layer syntax
        arcpy.MakeFeatureLayer_management(basin_boundary, 'GBM_layer',
                                          """ "Identifier" = '{}' """.format(catchment))

        # Selecting feature by location
        arcpy.SelectLayerByLocation_management('points_layer', 'COMPLETELY_WITHIN', 'GBM_layer')

        # converting the feature layer into feature class(shape file)
        arcpy.FeatureClassToFeatureClass_conversion('points_layer', out_path, "{}".format(catchment))

        # Adding field to the shape file

        # Splitting the shape file path to crate the file path list
        shp_file_path = r"{}\{}.shp".format(out_path, catchment)
        shp_path_list = shp_file_path.split(os.sep)
        layer_name = shp_path_list[-1][:-4]

        # Adding field named as "Remarks" to shape file
        field = 'Remarks'
        arcpy.AddField_management(shp_file_path, field, 'TEXT')

        # Creating a points feature layer from the points shape file
        arcpy.MakeFeatureLayer_management(shp_file_path, '{}'.format(layer_name))

        # Using search cursor updating each row of added new field
        with arcpy.da.UpdateCursor('{}'.format(layer_name), ['Remarks']) as u_cursor:
            for row in u_cursor:
                row[0] = shp_path_list[-1][:-4]
                u_cursor.updateRow(row)

        # Deleting blank shape file if it is empty
        if int(arcpy.GetCount_management('{}'.format(layer_name)).getOutput(0)) == 0:
            arcpy.Delete_management(shp_file_path)

            arcpy.FeatureClassToFeatureClass_conversion('GBM_layer', out_path, '{}'.format(catchment))

            blank_catchment_polygon_shp = os.path.join(out_path, '{}.shp'.format(catchment))
            blank_projection_shp_path = blank_basin_projection(point_shp_file, blank_catchment_polygon_shp,
                                                               out_path)
            without_points_shp_path_list.append(blank_projection_shp_path)
            arcpy.Delete_management(blank_catchment_polygon_shp)

        else:
            with_points_shp_path_list.append(shp_file_path)

    # Merging all shape file to create a merged shape file
    arcpy.Merge_management(with_points_shp_path_list,
                           r"{}\Merged\{}_with_grid_points.shp".format(out_folder, point_shp_path_list[-1][:-4]))

    arcpy.Merge_management(without_points_shp_path_list,
                           r"{}\Merged\{}_without_grid_points.shp".format(out_folder, point_shp_path_list[-1][:-4]))

    print(point_shp_path_list[-1][:-4])
