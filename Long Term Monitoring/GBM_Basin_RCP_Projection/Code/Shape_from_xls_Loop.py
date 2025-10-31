import os
import glob
import arcpy

arcpy.env.overwriteOutput = True

# Setting the spatial reference of Shape Files
spatial_reference = r"E:\Script\GBM_Basin_RCP_Projection\Input_Data\WGS 1984.prj"

# Setting the sheet name in xls file from which shape file will be created
sheet_name = "Sheet1"

# Setting the output shape file folder
output_folder_path = r"E:\Script\GBM_Basin_RCP_Projection\Output\Gridded_data_shape"

for excel_file in glob.glob(r"E:\Script\GBM_Basin_RCP_Projection\Output\Processed_Gridded_Data\**\*_combined.xls"):

    # Setting the folder path of xls file and sheet name
    xls_file_path = excel_file

    # Separating the file path to create the file path list
    path_list = excel_file.split(os.sep)

    # Setting the local variables
    in_table = r"{}\{}.dbf".format(output_folder_path, 'Gridded_Data')
    x_coordinate = "Longitude"
    y_coordinate = "Latitude"
    out_layer = "{}".format(path_list[-1][:-4])

    # excel to table conversion
    arcpy.ExcelToTable_conversion(xls_file_path, in_table, Sheet=sheet_name)

    # Making the XY Event layer
    arcpy.MakeXYEventLayer_management(in_table, x_coordinate, y_coordinate, out_layer, spatial_reference)

    # Shape file output folder path with name
    shp_file = r"{}\{}".format(output_folder_path, path_list[-1][:-4])
    arcpy.CopyFeatures_management(out_layer, shp_file)

    # Removing the created layer (useful/necessary while iterating)
    del out_layer

    # Deleting the created table
    arcpy.Delete_management(in_table)

    print(path_list[-1][:-4])
