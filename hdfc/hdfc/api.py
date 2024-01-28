import frappe
import json
from frappe.utils.file_manager import save_file
import zipfile
from io import BytesIO

@frappe.whitelist(allow_guest=True)
def ping():
    return 'pong'

@frappe.whitelist(allow_guest=True)
def docData():
    doc = frappe.get_doc('Common Instruction Form', 'cf2266ac07')
    return doc

@frappe.whitelist(allow_guest=True)
def postData():
    doc = frappe.get_doc({
    'doctype': 'Common Instruction Form',
    'title': 'New Task'
    })
    doc.customer_id="1234567"
    doc.account_no="7475y394"
    doc.insert()
    return frappe.get_meta('Common Instruction Form')

@frappe.whitelist(allow_guest=True)
def bodyData():
    raw_data = frappe.request.get_data(as_text=True)
    json_data = json.loads(raw_data)
    return json_data

@frappe.whitelist(allow_guest=True)
def paramData():
    raw_data = frappe.request.get_data(as_text=True)
    json_data = json.loads(raw_data)
    return json_data
    # param_data=frappe.local.form_dict
    # return param_data

@frappe.whitelist(allow_guest=True)
def attachFilet():
    binary_data = frappe.request.get_data(as_text=False)

    zip_data = BytesIO(binary_data)

    with zipfile.ZipFile(zip_data, 'r') as zip_file:
        file_list = zip_file.namelist()
        for file_name in file_list:
            file_content = zip_file.read(file_name)
            save_file(file_name, file_content, 'Common Instruction Form', 'cf2266ac07')

    return "Files are extracted and attached successfully"