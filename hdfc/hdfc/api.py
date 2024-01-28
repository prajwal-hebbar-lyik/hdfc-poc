import json
import base64
import frappe
from frappe import db as db
from frappe.client import attach_file


def is_base64(s: str) -> bool:
    try:
        s_bytes = bytes(s, "ascii")
        return base64.b64encode(base64.b64decode(s_bytes)) == s_bytes
    except Exception as ex:
        print(ex)
        return False


def get_common_fields(lyikrec: dict) -> dict:
    rec = lyikrec
    doc_rec = {}
    doc_rec["submitter_phone"] = rec["_submitter_phone"]
    doc_rec["submission_time"] = rec["submission_time"]

    if "receipt_url" in rec:
        doc_rec["receipt_url"] = rec["receipt_url"]

    if "record_id" in rec:
        doc_rec["lyik_id"] = rec["record_id"]

    if "mobile_otp" in rec and rec["mobile_otp"] != None:
        doc_rec["digital_signature_type"] = "Mobile"
        doc_rec["digital_signature_id"] = rec["mobile_otp"]
    elif "email_otp" in rec and rec["email_otp"] != None:
        doc_rec["digital_signature_type"] = "Email"
        doc_rec["digital_signature_id"] = rec["email_otp"]
    elif "aadhaar_uid_sign" in rec and rec["aadhaar_uid_sign"] != None:
        doc_rec["digital_signature_type"] = "Aadhaar"
        doc_rec["digital_signature_id"] = rec["aadhaar_uid_sign"]

    return doc_rec


def translate_to_consent_withdrawal_form(rec: dict) -> dict:
    # mapping of <doctype field>:<lyik field>
    field_mapping = {
        "full_name": "customer_name",
        "mobile_number": "mobile_number",
        "name_passport": "passport_fullname",
        "passport_number": "passport_number",
        "name_voter_id": "voterid_fullname",
        "voter_id_number": "voterid_number",
        "name_dl": "dl_fullname",
        "dl_number": "dl_number",
        "name_aadhaar": "aadhaar_fullname",
        "aadhaar_number": "aadhaar_number",
        "name_pan": "pan_fullname",
        "pan_number": "pan_number",
    }

    doc_rec = {}
    for doc_f in field_mapping:
        lyik_f = field_mapping[doc_f]
        if lyik_f in rec:
            doc_rec[doc_f] = rec[lyik_f]

    # The list below are the 'products' booleans in the DocType
    binaries = [
        "deposit",
        "cards",
        "account",
        "loan",
        "investment",
        "insurance",
        "prepaid_cards",
        "mercahant_solutions",
        "working_capital",
        "pay_zapp",
    ]
    for b in binaries:
        doc_rec[b] = 1 if b in rec["products"] else 0

    doc_rec.update(get_common_fields(rec))

    return doc_rec


def translate_to_common_instruction_form(rec: dict) -> dict:
    # mapping of <doctype field>:<lyik field>
    field_mapping = {
        "customer_id": "customer_id",
        "account_no": "account_no",
        "statement_from": "statement_from",
        "statement_to": "statement_to",
        "int_cert_from": "int_cert_from",
        "int_cert_to": "int_cert_to",
        "fd_no": "fd_no",
        "form16a_year": "form16a_year",
        "cheque_no": "cheque_no",
        "dispatch_mode": "dispatch_mode",
        "other_person_mobile_number": "other_person_mobile_number",
        "mailing_address": "mailing_address",
        "deposit_number": "deposit_number",
        "means_to_credit": "means_to_credit",
        "deposit_owner": "deposit_owner",
        "balance_confirmation": "balance_confirmation",
        "fd_balances": "fd_balances",
        "passbook_consent": "passbook_consent",
    }

    doc_rec = {}
    for doc_f in field_mapping:
        lyik_f = field_mapping[doc_f]
        if lyik_f in rec:
            doc_rec[doc_f] = rec[lyik_f]

    doc_rec.update(get_common_fields(rec))

    return doc_rec


def translate_to_name_consent_form(rec: dict) -> dict:
    # mapping of <doctype field>:<lyik field>
    field_mapping = {
        "customer_id": "customer_id",
        "customer_name": "customer_name",
        "reason_for_change": "reason_for_change",
        "new_name": "new_name",
        "short_name": "short_name",
        "nature_of_business": "nature_of_business",
        "details_of_activity": "details_of_activity",
        "annual_turnover": "annual_turnover",
        "iec_code": "iec_code",
        "value_of_import_export": "value_of_import_export",
        "nature_of_industry": "nature_of_industry",
    }

    doc_rec = {}
    for doc_f in field_mapping:
        lyik_f = field_mapping[doc_f]
        if lyik_f in rec:
            doc_rec[doc_f] = rec[lyik_f]

    doc_rec["is_non_profit"] = (
        1 if ("is_non_profit" in rec and rec["is_non_profit"] == "Yes") else 0
    )
    doc_rec["import"] = (
        1 if ("import_export" in rec and "import" in rec["import_export"]) else 0
    )
    doc_rec["export"] = (
        1 if ("import_export" in rec and "export" in rec["import_export"]) else 0
    )
    doc_rec["owned"] = (
        1 if ("address_type" in rec and "owned" in rec["address_type"]) else 0
    )
    doc_rec["rented_leased"] = (
        1 if ("address_type" in rec and "rented_leased" in rec["address_type"]) else 0
    )

    doc_rec.update(get_common_fields(rec))

    return doc_rec


def get_doctype_record(doctype: str, rec: dict) -> dict:
    if doctype == "Consent Withdrawal Form":
        return translate_to_consent_withdrawal_form(rec)
    elif doctype == "Common Instruction Form":
        return translate_to_common_instruction_form(rec)
    elif doctype == "Name Consent Form":
        return translate_to_name_consent_form(rec)

    rec.update(get_common_fields(rec))
    return rec


def add_attachment(key, doctype, file_name, file_data):
    file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": file_name,
            "attached_to_doctype": doctype,
            "attached_to_name": key,
            "attached_to_field": None,
            "folder": None,
            "is_private": None,
            "content": file_data,
            "decode": True,
        }
    )
    file.save()


def query_name_on_lyik_id(doctype, id) -> str:
    # here name means the ID of the record within the DocType
    recs = db.get_list(doctype, filters={"lyik_id": id}, pluck="name")
    return recs[0]


@frappe.whitelist()
def lyik_insert_record(**kwargs):
    """
    This function expects the following keyword values
    record : contains a JSON document that contains all the fields that need to be inserted into the doctype
    operation : contains the nature of operation. It can be 'INSERT' or 'UPDATE'
    doctype : The name of the doctype. Example: 'Common Instruction Form'
    <filename> : base64 encoded bytes of the file. All the other arguments are assumed to be files that will be attached to the document
    """
    is_insert = kwargs["operation"] == "INSERT"
    is_update = kwargs["operation"] == "UPDATE"

    print(f'Operation is {kwargs["operation"]}')
    doctype = kwargs["doctype"]

    if is_insert:
        record = get_doctype_record(doctype, json.loads(kwargs["record"]))
        record["doctype"] = doctype
        cif = frappe.get_doc(record)
        newrec = cif.insert(ignore_permissions=True)
        # Now store the primary key
        pkey = newrec.name

    if is_update:
        lyik_id = kwargs["record_id"]
        pkey = query_name_on_lyik_id(doctype, lyik_id)
        print(f"Lyik ID -> {lyik_id}. DocType name -> {pkey}")

    # Parse through the input to insert files if any
    for k in kwargs:
        v = kwargs[k]
        print(f"Trying to insert {k}")
        if is_base64(v):
            print(f"{k} is detected as a file")
            add_attachment(key=pkey, doctype=doctype, file_name=k, file_data=v)

    return f"Successfully added a new document with the ID {pkey}"
