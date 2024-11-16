import frappe

@frappe.whitelist()
def set_medication_order_instructions(patient_encounter_name):
    try:
        # Fetch the Patient Encounter document
        patient_encounter = frappe.get_doc('Patient Encounter', patient_encounter_name)

          # Extract drug_prescription details
        drug_prescriptions = [
            {
                "medication": drug.medication,
                "comment": drug.comment
            }
            for drug in patient_encounter.drug_prescription
        ]

        return {
            "status": "success",
            "drug_prescription": drug_prescriptions
        }
    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "message": "Patient Encounter or Inpatient Medication Order not found."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
