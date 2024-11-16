import frappe
from frappe import _

# Function to fetch clinical procedure details
@frappe.whitelist()
def fetch_clinical_procedure_details(patient_name):
    patient = frappe.get_doc('Patient', patient_name)
    clinical_procedures_list = []
    clinical_procedures = []

    if patient.name:
        clinical_procedures = frappe.get_all("Clinical Procedure",
                                             filters={"patient": patient_name, "custom_procedure_invoiced": 0},
                                             fields=["name", "procedure_template"])
        for cp in clinical_procedures:
            clinical_procedure_template = frappe.get_doc("Clinical Procedure Template",
                                                          cp.procedure_template)
            if clinical_procedure_template.is_billable:
                item = clinical_procedure_template.item
                rate = clinical_procedure_template.rate
                clinical_procedures_list.append({
                    "item_code": item,
                    "rate": rate,
                    "qty": 1,
                    # Add other relevant fields
                })

        frappe.session['clinical_procedures_list'] = clinical_procedures_list
     
    return clinical_procedures_list


def update_custom_procedure_invoiced(doc, method):
    SI = frappe.get_doc("Sales Invoice", doc.name)
    # frappe.msgprint(_(str(SI.patient)))
    for item in SI.items:
           
    #    frappe.msgprint(_(str(item.item_name)))
       if item.item_name:
            clinical_procedure = frappe.get_all("Clinical Procedure",
                                                 filters={"patient": SI.patient,
                                                          "procedure_template": item.item_name},
                                                 fields=["name"])
            if clinical_procedure:
                frappe.db.set_value("Clinical Procedure", clinical_procedure[0].name,
                                    "custom_procedure_invoiced", 1)
                frappe.msgprint(_(str(SI.patient_name)+"'s procedures Invoiced"))
                
import frappe
@frappe.whitelist()
def generate_customer_sales_summary(customer):
    invoices = frappe.get_list('Sales Invoice', filters={'customer': customer, 'docstatus': 1}, fields=['name', 'outstanding_amount', 'grand_total', 'posting_date', 'patient_name'])
    pdf_data = []

    total_outstanding_amount = 0
    total_grand_total = 0
    total_amount = 0  # Total amount of all items in all invoices

    seen = set()  # Keep track of seen invoice names
    for invoice in invoices:
        if invoice['name'] not in seen:
            invoice_items = []
            invoice_doc = frappe.get_doc('Sales Invoice', invoice['name'])
            for item in invoice_doc.items:
                invoice_items.append({
                    'Item Code': item.item_code,
                    'Item Name': item.item_name,
                    'Qty': item.qty,
                    'Rate': item.rate,
                    'Amount': item.amount
                })

                total_amount += item.amount  # Add the amount of each item to the total amount

            pdf_data.append({
                'Invoice': invoice['name'],
                'Outstanding Amount': invoice['outstanding_amount'],
                'Grand Total': invoice['grand_total'],
                'Posting Date': invoice['posting_date'],
                'Patient Name': invoice['patient_name'],
                'Items': invoice_items
            })
            total_outstanding_amount += invoice['outstanding_amount']
            total_grand_total += invoice['grand_total']

            seen.add(invoice['name'])

    pdf_data.append({
        'Total Outstanding Amount': total_outstanding_amount,
        'Total Grand Total': total_grand_total,
        'Total Amount': total_amount
    })

    return pdf_data


import frappe

@frappe.whitelist()
def generate_all_customer_sales_summary(customer):
    # Get sales invoices for the customer
    invoices = frappe.get_list(
        'Sales Invoice', 
        filters={'customer': customer, 'docstatus': 1}, 
        fields=['name', 'outstanding_amount', 'grand_total', 'posting_date', 'patient_name', 'patient']
    )
    
    # Initialize PDF data and summary totals
    pdf_data = []
    total_outstanding_amount = 0
    total_grand_total = 0
    total_amount = 0  # Total amount of all items in invoices and pharmacy

    seen_invoices = set()  # Track processed invoices
    for invoice in invoices:
        if invoice['name'] not in seen_invoices:
            invoice_items = []
            invoice_doc = frappe.get_doc('Sales Invoice', invoice['name'])
            
            # Collect items in each invoice
            for item in invoice_doc.items:
                invoice_items.append({
                    'Item Code': item.item_code,
                    'Item Name': item.item_name,
                    'Qty': item.qty,
                    'Rate': item.rate,
                    'Amount': item.amount
                })
                total_amount += item.amount  # Sum up invoice item amounts
            
            # Add invoice details to PDF data
            pdf_data.append({
                'Invoice': invoice['name'],
                'Outstanding Amount': invoice['outstanding_amount'],
                'Grand Total': invoice['grand_total'],
                'Posting Date': invoice['posting_date'],
                'Patient Name': invoice['patient_name'],
                'Items': invoice_items
            })
            total_outstanding_amount += invoice['outstanding_amount']
            total_grand_total += invoice['grand_total']
            seen_invoices.add(invoice['name'])

    # Fetch all draft pharmacy entries for patients from the invoices
    seen_pharmacy = set()  # Track processed pharmacy entries
    for invoice in invoices:
        # Fetch pharmacy items for each patient in draft status (docstatus = 0)
        pharmacy_items = frappe.get_list(
            'Pharmacy', 
            filters={'patient': invoice['patient'], 'docstatus': 0}, 
            fields=['name']
        )
        
        for pharm_item in pharmacy_items:
            if pharm_item['name'] not in seen_pharmacy:
                pharmacy_doc = frappe.get_doc('Pharmacy', pharm_item['name'])
                pharmacy_item_details = []
                
                # Collect all drug prescription details from each pharmacy entry
                for item_detail in pharmacy_doc.drug_prescription:
                    pharmacy_item_details.append({
                        'Drug Code': item_detail.drug_code,
                        'Drug Name': item_detail.drug_name,
                        'Qty': item_detail.qty,
                        'Rate': item_detail.rate,
                        'Amount': item_detail.amount
                    })
                    total_amount += item_detail.amount  # Sum up prescription item amounts
                
                # Append pharmacy data to the overall PDF data, including the items
                pdf_data.append({
                    'Pharmacy': pharm_item['name'],
                    'Patient Name': pharmacy_doc.patient,
                    'Prescription Items': pharmacy_item_details
                })
                seen_pharmacy.add(pharm_item['name'])

    # Append total summary at the end of PDF data
    pdf_data.append({
        'Total Outstanding Amount': total_outstanding_amount,
        'Total Grand Total': total_grand_total,
        'Total Amount': total_amount
    })

    return pdf_data
