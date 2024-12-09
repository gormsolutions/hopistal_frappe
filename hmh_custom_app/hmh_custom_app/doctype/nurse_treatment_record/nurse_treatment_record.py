from frappe.model.document import Document
import frappe
from frappe import _

class NurseTreatmentRecord(Document):
    def on_update(self):
        try:
            # Fetch the Patient document
            patient_doc = frappe.get_doc('Patient', self.patient)
            patient_reg = frappe.get_doc('Patient Registration Identification', patient_doc.custom_patient_mrno)

            # Check for an existing Pharmacy document in draft status
            pharmacy_docs = frappe.get_all(
                'Pharmacy',
                filters={'treatment_id': self.name, 'docstatus': 0},  # docstatus 0 means draft
                fields=['name']
            )

            if pharmacy_docs:
                # If a draft Pharmacy document exists, update it
                pharmacy_doc = frappe.get_doc('Pharmacy', pharmacy_docs[0].name)

                # Create a mapping of current drug prescriptions for easy access
                current_drugs = {item.drug_code: item for item in pharmacy_doc.drug_prescription}

                # Update or append drug prescription items
                for drug in self.medication_administered:
                    existing_treatment_item = current_drugs.get(drug.medication_name)

                    if existing_treatment_item:
                        # Check and update fields if there are changes
                        changes_made = False
                        if (existing_treatment_item.dosage != drug.dosage or
                            existing_treatment_item.period != drug.period or
                            existing_treatment_item.dosage_form != drug.dosage_form):
                            
                            # Update only the changed fields
                            existing_treatment_item.dosage = drug.dosage
                            existing_treatment_item.period = drug.period
                            existing_treatment_item.dosage_form = drug.dosage_form
                            changes_made = True

                        # # Optionally log changes
                        # if changes_made:
                        #     frappe.msgprint(_("Updated prescription for: {0}").format(drug.medication_name))

                    else:
                        # Append new drug prescription item if it doesn't exist
                        pharmacy_doc.append("drug_prescription", {
                            "drug_code": drug.medication_name,
                            "dosage": drug.dosage,
                            "period": drug.period,
                            "qty": 1,
                            "dosage_form": drug.dosage_form
                        })

                # Remove drug prescriptions that are no longer present
                drugs_to_remove = [item for item in pharmacy_doc.drug_prescription if item.drug_code not in {drug.medication_name for drug in self.medication_administered}]
                for item in drugs_to_remove:
                    pharmacy_doc.drug_prescription.remove(item)

            else:
                # If no draft exists, create a new Pharmacy document
                pharmacy_doc = frappe.new_doc('Pharmacy')
                pharmacy_doc.update({
                    "patient": self.patient,
                    "patient_sex": patient_doc.sex,
                    "patient_age": patient_reg.full_age,
                    "encounter_date": self.treatment_start_date,
                    "practitioner": patient_doc.custom_consulting_doctor,
                    "treatment_id": self.name,
                    "inpatient_record": self.inpatient_admission,
                    "medical_department": patient_doc.custom_consulting_department
                })

                # Append drug prescription items to the new Pharmacy document
                for drug in self.medication_administered:
                    pharmacy_doc.append("drug_prescription", {
                        "drug_code": drug.medication_name,
                        "dosage": drug.dosage,
                        "period": drug.period,
                        "qty": 1,
                        "dosage_form": drug.dosage_form
                    })

                # Insert the new Pharmacy document and commit the changes
                pharmacy_doc.insert(ignore_permissions=True)

            # Save the Pharmacy document
            pharmacy_doc.save(ignore_permissions=True)

        except frappe.DoesNotExistError as e:
            frappe.log_error(f"Document not found: {str(e)}", "create_pharmacy Error")
            frappe.throw(_("The specified document was not found."))

        except Exception as e:
            # Log and throw any other exceptions
            frappe.log_error(f"Error in creating or updating Pharmacy document: {str(e)}", "create_pharmacy Error")
            frappe.throw(_("There was an error creating or updating the Pharmacy document."))
