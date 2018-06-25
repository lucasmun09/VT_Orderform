#! /usr/bin/python

import csv
import pdfrw
import datetime
from datetime import timedelta
# max of 25 characters

INVOICE_TEMPLATE_PATH = 'blank.pdf'
INVOICE_OUTPUT_PATH = 'test.pdf'

NEEDED_BY = 7  # Needed by (today + number of days)

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
    vendor_dict = {}
    for vendor in input_list:
        vendor_dict[vendor[0]] = {
            'Vendor': vendor[0],
            'Address 1': vendor[1],
            'Address 2': vendor[3] + ", " + vendor[4] + " " + vendor[5],
            'Phone_2': vendor[6],
            'Fax': vendor[7],
            'Date of Request': date_today,
            'Date Needed': date_needed
        }

    return vendor_dict


# TODO: Wrong logic flow
def set_request_dict(input_list):
    request_dict = {}
    for index, row in enumerate(input_list):
        request_dict['QtyRow' + str(index + 1)] = row[2]
        request_dict['Unit EaPkgFtRow' + str(index + 1)] = row[3]
        request_dict['Item Number  Item descriptionRow' + str(index + 1)] = row[4]
        request_dict['Cost per UnitRow' + str(index + 1)] = row[5]
        try:
            request_dict['TotalRow' + str(index + 1)] = str(round(float(row[2]) * float(row[5]), 2))
        except:
            print("serror")
    return request_dict


# opens csv files and removes the first line (usually the header)
def open_csv(csv_location):
    with open(csv_location, 'rU') as f:
        requests = csv.reader(f)
        next(requests)
        data_requests = [r for r in requests]
    return data_requests


# returns all of the vendors present in the request form
def return_vendors(input_list):
    unique_vendors = set()
    for row in input_list:
        unique_vendors.add(row[1])
    return unique_vendors


# todo, create a new page if there is more than 10 item in a vendor
def generate_page_data(raw_requests, vendor_dict): # With the given raw requests, it will put the requests in separate list
    pages_data = {}
    for request in raw_requests:
        if not request[1] in pages_data:
            pages_data[request[1]] = [[request]]
        else:
            pages_data[request[1]][-1].append(request)

    pages = []


    for vendor in vendor_dict:
        if vendor in pages_data:
            for vendor in pages_data[vendor]:
                for page in vendor:
                    payload_dict = {**set_request_dict(vendor), **set_request_dict(page)}
                    #pages.append({** set_request_dict(vendor), **set_request_dict(page)})
                    pages.append(payload_dict)

                    print("")
        print("")
    #print(pages)


    return pages

def main():
    # write_fillable_pdf(INVOICE_TEMPLATE_PATH, INVOICE_OUTPUT_PATH, data_dict)
    request_data = open_csv("requests.csv")    # timestamp, vendor, qty, unit, item, cost, comment
    vendor_data = open_csv("vendors.csv")    # vendor, street, city, state,zip,phone,fax
    # payload_dict = {**request_dict, **vendor_dict} # combine requests fields and vendor fields into one

    pages_data = generate_page_data(request_data, set_vendor_dict(vendor_data))


if __name__ == '__main__':
    main()