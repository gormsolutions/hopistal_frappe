import frappe

@frappe.whitelist()
def create_vital_signs_for_patient(doc_name):
    # Check if a draft Vital Signs document already exists for this patient
    existing_vital_signs = frappe.get_all("Vital Signs", filters={
        "patient": doc_name,
        "custom_patient_status": "Seen The Receptionist",
        "docstatus": 0  # Ensure it's in draft state
    })

    if not existing_vital_signs:
        # Create a new Vital Signs document in draft state
        try:
            vital_signs = frappe.get_doc({
                "doctype": "Vital Signs",
                "patient": doc_name,
                "custom_practionaer": frappe.get_doc("Patient", doc_name).custom_consulting_doctor,
                "custom_patient_status": "Seen The Receptionist",
                "custom_customer_type": frappe.get_doc("Patient", doc_name).customer_group,
                "custom_invoice_no": frappe.get_doc("Patient", doc_name).custom_invoice_no,
            })
            vital_signs.insert(ignore_permissions=True)
            return "Vital Signs created successfully."
        except Exception as e:
            frappe.log_error(f"Failed to create Vital Signs for patient {doc_name}: {str(e)}", "Vital Signs Creation Error")
            return f"Error: {str(e)}"
    else:
        return "Vital Signs document already exists."
