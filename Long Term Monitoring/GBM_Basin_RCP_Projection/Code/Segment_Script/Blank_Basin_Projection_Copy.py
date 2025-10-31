import arcpy
import os
import glob

arcpy.env.overwriteOutput = True

# Setting the path of gridded points data shape file
gridded_points_shp = r"E:\Script\Pycharm_Code\GBM_Basin_Blank_Catchment\Gridded_Data\Base_Temperature_Gridded.shp"
arcpy.MakeFeatureLayer_management(gridded_points_shp, 'Gridded_Points_layer')
gridded_points_path_list = gridded_points_shp.split(os.sep)

# Setting the output folder path
output_path = r"E:\Script\Pycharm_Code\GBM_Basin_Blank_Catchment\Output"

# Iterating through the blank shape file folder
for shp_file in glob.glob(r"E:\Script\Pycharm_Code\GBM_Basin_Blank_Catchment\Basin_Boundary\No_Points\*.shp"):

    # Setting the path of the catchment area polygon feature
    catchment_area_shp = shp_file
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
        outFields = "ALL"
        arcpy.CreateThiessenPolygons_analysis('Gridded_Points_layer', thiessen_polygon_feature, outFields)


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
    area_weightage_field = ['Area_sqkm', 'Weightage', 'Remaraks']
    field_type = ['DOUBLE', 'DOUBLE', 'TEXT']

    # Iterating through the list and adding the fields in the shape file (field type: DOUBLE)
    for field, f_type in zip(area_weightage_field,field_type):
        arcpy.AddField_management('clipped_Area_layer', field, f_type)


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
        for row in cursor:
            weightage = row[0] / catchment_area
            row[1] = weightage
            row[2] = catchment_area_shp_path_list[-1][:-4]
            cursor.updateRow(row)

    print(catchment_area_shp_path_list[-1][:-4])
