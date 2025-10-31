import arcpy
import pandas as pd
import os
import glob

arcpy.env.overwriteOutput = True

# Setting file path of GBM catchment shape file
basin_boundary = r"E:\Script\Pycharm_Code\GBM_Basin\Input_Data\Basin_Boundary\GBM_WGS84.shp"

# Setting the output folder path
out_folder = r"E:\Script\Pycharm_Code\GBM_Basin\Output"

# Reading the GBM Basin catchment list file
c_df = pd.read_csv(r"E:\Script\Pycharm_Code\GBM_Basin\Input_Data\GBM_Basin_Catchment_List.csv")

for point_shp_file in glob.glob(r"E:\Script\Pycharm_Code\GBM_Basin\Input_Data\Input_Data\*.shp"):

    # Splitting the point shape file path to create a path list
    point_shp_path_list = point_shp_file.split(os.sep)

    # Creating a new folder to store the shape file
    out_path = os.path.join(out_folder, "{}".format(point_shp_path_list[-1][:-4]))
    os.mkdir(out_path)

    # Setting folder path of gridded points shape file
    points_shp = point_shp_file

    # Creating a points feature layer from points shape file
    arcpy.MakeFeatureLayer_management(points_shp, 'points_layer')

    # Creating a list to store the created shape file
    shp_list = []

    for catchment in c_df['Catchment_ID']:

        # Creating feature layer from shape file to use as input file in selection by layer syntax
        arcpy.MakeFeatureLayer_management(basin_boundary, 'GBM_layer', """ "Identifier" = '{}' """.format(catchment))

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

        else:
            shp_list.append(shp_file_path)

    # Merging all shape file to create a merged shape file
    arcpy.Merge_management(shp_list, r"E:\Script\Pycharm_Code\GBM_Basin\Output\Merged\{}.shp"
                           .format(point_shp_path_list[-1][:-4]))

    print(point_shp_path_list[-1][:-4])
