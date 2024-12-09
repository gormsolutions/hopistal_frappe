import frappe

@frappe.whitelist()
def create_inpatient_admission_on_save(patient, encounter_date, practitioner):
    # Check if there's an existing admission for the patient
    existing_admission = frappe.get_all("Inpatient Admission", filters={
        "patient_id": patient,
        "status": ["!=", "Discharged"]
    })

    if not existing_admission:
        # Create new Inpatient Admission if one doesn't exist
        admission = frappe.get_doc({
            "doctype": "Inpatient Admission",
            "patient_id": patient,
            "admission_date": encounter_date,
            "attending_doctor": practitioner,
            "admission_status": "Admission Scheduled"
        })
        
        # Save the Inpatient Admission
        admission.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"message": "Inpatient Admission created successfully."}
    else:
        return {"message": "An admission already exists for this patient."}
