import frappe
from frappe import _

@frappe.whitelist()
def create_sales_invoice(patient_encounter):
    # Get the patient information from the Patient Encounter
    patient_encounter_doc = frappe.get_doc("Patient Encounter", patient_encounter)
    patient = patient_encounter_doc.patient
    # Fetch the patient document linked in the Patient Encounter
    patient_doc = frappe.get_doc("Patient", patient_encounter_doc.patient)

    # Check if a Sales Invoice already exists for the patient
    existing_invoice = frappe.db.exists("Sales Invoice", {"patient": patient, "docstatus": 0})
    if existing_invoice:
        return {
            "message": _("A sales invoice already exists for this patient.")
        }

    # Create a Sales Invoice
    sales_invoice = frappe.new_doc("Sales Invoice")
    sales_invoice.patient = patient
    sales_invoice.company = frappe.defaults.get_global_default("company")
    sales_invoice.customer = patient_doc.customer
    sales_invoice.due_date = frappe.utils.data.add_days(frappe.utils.nowdate(), 30)
    sales_invoice.set_posting_time = 1
    sales_invoice.posting_date = frappe.utils.nowdate()
    sales_invoice.due_date = frappe.utils.add_days(frappe.utils.nowdate(), 30)
    sales_invoice.append("items", {
        "item_code": patient_encounter_doc.custom_consultation,
        "rate": patient_encounter_doc.custom_fee,
        "qty": 1
    })

    # # Save the Sales Invoice as draft
    # sales_invoice.save(ignore_permissions=True)
    # Save the Sales Invoice
    sales_invoice.insert()

    # Submit the Sales Invoice
    sales_invoice.submit()

    return {
        "sales_invoice_name": sales_invoice.name,
        "message": _("Sales Invoice {0} created and submited successfully.").format(sales_invoice.name)
    }

@frappe.whitelist()
def copy_items_from_bundle(procedure_name):
    procedure = frappe.get_doc('Clinical Procedure', procedure_name)
    
    if not procedure.procedure_template:
        frappe.throw('Procedure Template is required in Clinical Procedure')
    
    product_bundle_name = procedure.procedure_template
    
    product_bundle = frappe.get_doc("Product Bundle", product_bundle_name)
    
    if not product_bundle:
        frappe.throw('Product Bundle not found for Procedure Template: ' + product_bundle_name)
    
    items = []
    for item in product_bundle.items:
        items.append({
            "item_code": item.item_code,
            "qty": item.qty,
            "uom": item.uom
        })
    
    return items






