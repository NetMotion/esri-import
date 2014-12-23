#
# Command line python script example for importing NetMotion Wireless
# coverage map CSV files into ESRI ArcMap
#
# Professional apology: I would normally archtect this into multiple files
# and a nice installer, but I wanted this to be a stand-alone example.
#

# To run I use: > c:\Python27\ArcGIS10.2\python.exe convert_netmo_csv_to_esri_shapefile.py

# Needed for command line support:
import sys
import getopt

# Needed for ESRI integration
import arcpy
import os

# Misc imports
import glob  # Needed to get a list of CSV files in the target dir
import csv   # CSV file handling package
import datetime  # date/time conversion

FILE_NAME = os.path.splitext(__file__)[0]

# This heredoc serves as something to print out for help (or in the case of
# bad params) but also as inline documentation of this utility
HELP = '''
Intro:
    %s
    A command line utility to convert one or more NetMotion Wireless
    coverage map CSV files into an ESRI shapefile
Usage:
    %s --shapefile file [--data directory]
Options:
    --help (or -h) : (optional) This message
    --shapefile (or -s) file : (optional) The ESRI Shapefile to save the data into
        (usually ends with '.shp')
        If not specified, defaults to current working dir + NetMotion.shp
    --input (or -i) directory : (optional) Path to a directory containing
        one or more NetMotion Wireless coverage map CSV files
        If not specified, defaults to current working directory
''' % (FILE_NAME, FILE_NAME)

def main(argv):
    data_dir = os.getcwd()  # default to the current working directory
    shapefile = "NetMotion.shp"  # defaults to current working directory + "NetMotion.shp"
    outpath = os.getcwd()
    arcpy.env.overwriteOutput = True
    try:
        opts, args = getopt.getopt(argv, "hs:d", ["shapefile=", "data", "help"])
    except getopt.GetoptError:
        print HELP
        sys.exit()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print HELP
            sys.exit()
        elif opt in ("-s", "--shapefile"):
            shapefile = arg
        elif opt in ("-i", "--input"):
            data_dir = arg
    # Grab the list of CSV files in the given directory
    csv_files = get_csv_file_list(data_dir)
    # Process all the CSV files found
    esri_headers = []  # mapping column numbers to ESRI-consumable strings
    netmo_data = []  # array to store all the rows we find while processing
    for csv_file in csv_files:
        # Crunch the data into one big array
        esri_headers, new_data_rows = process_csv_file(csv_file)
        netmo_data = netmo_data + new_data_rows
    # Convert the data into ESRI's Shapefile format and save it
    save_netmo_data_as_shapefile(esri_headers, netmo_data, shapefile, outpath)


def get_csv_file_list(data_dir):
    target_files = os.path.join(data_dir, '*.csv')
    csv_files = glob.glob(target_files)
    return csv_files


def process_csv_file(csv_file):
    data_rows = []
    with open(csv_file, 'rU') as file_handle:
        file_index = csv.reader(file_handle, delimiter=',')
        esri_headers = []
        for i, row in enumerate(file_index):
            if i == 0:
                for j, col in enumerate(row):
                    esri_headers.append(clean_esri_header_string(col))
            else:
                new_row = convert_netmo_row_to_dict(esri_headers, row)
                data_rows.append(new_row)
    return esri_headers, data_rows


def save_netmo_data_as_shapefile(esri_headers, netmo_data, shapefile, outpath):
    coordinate_system = "WGS 1984"
    # arcpy.CreateFeatureclass_management(outpath, shapefile, "POINT", spatial_reference=coordinate_system)  # display segments as points
    arcpy.CreateFeatureclass_management(outpath, shapefile, "POLYLINE", spatial_reference=coordinate_system)  # display segments as lines
    # Tell ESRI about each column (name and type)
    for esri_header in esri_headers:
        esri_header_type = get_esri_header_type(esri_header)
        arcpy.AddField_management(shapefile, esri_header, esri_header_type)
    # Create one ESRI row for each NetMo row
    cursor = arcpy.InsertCursor(shapefile, coordinate_system)
    id = 0
    for netmo_row in netmo_data:
        esri_row = cursor.newRow()
        x1 = y1 = x2 = y2 = None
        for header, value in netmo_row.iteritems():
            if value is not None:
                esri_row.setValue(header, value)
                if header == "StartLong":
                    x1 = value
                elif header == "StartLati":
                    y1 = value
                elif header == "EndLongit":
                    x2 = value
                elif header == "EndLatitu":
                    y2 = value
        if x1 is not None:
            poly_line = arcpy.Array()
            poly_line.add(arcpy.Point(x1, y1))
            poly_line.add(arcpy.Point(x2, y2))
            # esri_row.shape = arcpy.Point(x1, y1)  # example where the shape is a point instead of a line
            esri_row.shape = poly_line
            esri_row.id = id
            id += 1
            cursor.insertRow(esri_row)  # Only insert rows for which we have lat/long data
        del esri_row
    del cursor
    pass


def save_netmo_data_as_csv(filename, esri_headers, netmo_data):
    with open(filename, 'w') as f:
        f_csv = csv.DictWriter(f, esri_headers)
        f_csv.writeheader()
        f_csv.writerows(netmo_data)
    pass


# To keep this utility script simple the converting of each row
# is an inelegant, bruteforce, hardcoded affair.
def convert_netmo_row_to_dict(esri_headers, row):
    new_row = {}
    for i, value in enumerate(row):
        esri_header = esri_headers[i]
        esri_header_type = get_esri_header_type(esri_header)
        value = value.strip()  # The end value on each CSV row has a EOL on it.  Kill that.
        if esri_header_type == "TEXT":
            new_row[esri_header] = value
        elif esri_header_type == "DATE":
            new_row[esri_header] = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        elif esri_header_type == "DOUBLE":  # the only floats are Lat/Long,  NetMo uses 0 to mean "no data"
            if value == "0" or value == "":
                new_row[esri_header] = None
            else:
                new_row[esri_header] = float(value)
        elif esri_header_type == "LONG":
            new_row[esri_header] = int(value)
    return new_row


def clean_esri_header_string(header_name):
    header_name = header_name.strip().replace(" ", "")  # ESRI does not allow any whitespace in or around header names
    header_name = header_name[0:9]  # ESRI does not allow field names greater than 10 chars
    return header_name


def get_esri_header_type(esri_header):
    # strings
    if esri_header in ("User", "Device", "LocalityU", "IMEI", "ESN", "MEI", "PhoneNumb", "Technolog", "HomeCarri", "RoamingCa", "RoamingSt"):
        return "TEXT"
    # dates
    elif esri_header in ("StartTime", "EndTimest"):
        return "DATE"
    # floats
    elif esri_header in ("StartLati", "EndLatitu", "StartLong", "EndLongit"):
        return "DOUBLE"
    # integers
    elif esri_header in ("NumberofS", "RSSI", "RSRP", "SINR", "RSRQ", "LocalityS"):
        return "LONG"
    return None


# Now that we have the main function defined, call it if python says
# this script is the main one
if __name__ == "__main__":
    main(sys.argv[1:])
