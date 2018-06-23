#! /usr/bin/python

import os
import csv
import pdfrw
import datetime
from datetime import timedelta
#max of 25 characters

INVOICE_TEMPLATE_PATH = 'blank.pdf'
INVOICE_OUTPUT_PATH = 'test.pdf'

NEEDED_BY = 7 # Needed by (today + number of days)

keys = []
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'

date_today = datetime.datetime.today().strftime('%m/%d/%Y')
diff = datetime.timedelta(days=NEEDED_BY) # seven days in future
date_needed = (datetime.datetime.now() + diff).strftime('%m/%d/%Y')


def write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict):
    global keys
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                keys.append(key)
                if key in data_dict.keys():
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                    )
        annotation.update(pdfrw.PdfDict(AP=''))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


# returns dict with given vendor data
def set_vendor_dict(input_list):
    # input_dict -> vendor, street, city, state,zip,phone,fax
    # these fields can only hold up to 16 characters without font decrease
    vendor_dict = {
        'Vendor' : input_list[0],
        'Address 1' : input_list[1],
        'Address 2' : input_list[3] + ", " + input_list[4] + " " + input_list[5],
        'Phone_2' : input_list[6],
        'Fax' : input_list[7],
        'Date of Request' : date_today,
        'Date Needed' : date_needed
    }
    return vendor_dict

def set_request_dict(input_list):
    request_dict = {}
    for index, row in enumerate(input_list):
        request_dict['QtyRow' + str(index + 1)] = row[2]
        request_dict['Unit EaPkgFtRow' + str(index + 1)] = row[3]
        request_dict['Item Number  Item descriptionRow' + str(index + 1)] = row[4]
        request_dict['Cost per UnitRow' + str(index + 1)] = row[5]
        request_dict['TotalRow' + str(index + 1)] = str(round(float(row[2]) * float(row[5]), 2))
    return request_dict


# returns all of the vendors present in the request form
def return_vendors(input_list):
    unique_vendors = set()
    for row in input_list:
        unique_vendors.add(row[1])


# opens csv files and removes the first line (usually the header)
def openCSV(csv_location):
    with open(csv_location) as f:
        requests = csv.reader(f)
        next(requests)
        data_requests = [r for r in requests]
    return data_requests

def main():
    # write_fillable_pdf(INVOICE_TEMPLATE_PATH, INVOICE_OUTPUT_PATH, data_dict)
    # timestamp, vendor, qty, unit, item, cost, comment
    request_data = openCSV("requests.csv")
    vendor_data = openCSV("vendors.csv")
    # vendor, street, city, state,zip,phone,fax

    request_dict = set_request_dict(request_data)
    print(request_dict)

    set_vendor_dict(vendor_data[1])
    return_vendors(request_data)

if __name__ == '__main__':
    main()