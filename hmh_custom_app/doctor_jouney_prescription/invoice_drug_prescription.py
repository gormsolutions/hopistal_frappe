import frappe
from frappe import _

def on_submit(doc, method):
    if not doc.drug_prescription:
        return

    try:
        # Fetch the Patient document
        patient_doc = frappe.get_doc('Patient', doc.patient)
        customer_doc = frappe.get_doc('Customer', patient_doc.customer)
        patient_reg_doc = frappe.get_doc('Patient Registration Identification', patient_doc.custom_patient_mrno)

        # Check for an existing draft Pharmacy doc for the same encounter
        existing_pharmacy_doc = frappe.get_all(
            "Pharmacy",
            filters={
                "patient_encounter_id": doc.name,
                "docstatus": 0  # Draft status
            },
            limit=1
        )

        if existing_pharmacy_doc:
            # Update the existing draft Pharmacy doc
            pharmacy_doc = frappe.get_doc("Pharmacy", existing_pharmacy_doc[0].name)
        else:
            # Create a new Pharmacy doc
            pharmacy_doc = frappe.new_doc("Pharmacy")

        # Initialize totals
        total_qty = 0
        total_amount = 0

        # Assign fields to the Pharmacy doc
        pharmacy_doc.update({
            "patient": doc.patient,
            "patient_sex": patient_doc.sex,
            "patient_age": patient_reg_doc.full_age,
            "encounter_date": doc.encounter_date,
            "practitioner": doc.practitioner,
            "price_list": patient_doc.default_price_list,
            "patient_encounter_id": doc.name,
            "medical_department": patient_doc.custom_consulting_department,
            "total_qty": total_qty,
            "total_amount": total_amount,
            "drug_prescription": []
        })

        # Flag to check if any item should be added
        has_items_to_add = False

        for item in doc.drug_prescription:
            if item.custom_drug_status == "Send to Pharmacy":
               continue
            
            # Append item to the Pharmacy doc
            pharmacy_doc.append("drug_prescription", {
                "drug_code": item.drug_code,
                "dosage": item.dosage,
                "period": item.period,
                "qty": item.custom_qty,
                "rate": item.custom_rate,
                "amount": item.custom_amount,
                "dosage_form": item.dosage_form,
                "strength": item.strength,
                "strength_uom": item.strength_uom,
            })

            # Update total quantities and amounts
            total_qty += item.custom_qty
            total_amount += item.custom_amount

            # Set the status to "Send to Pharmacy"
            item.custom_drug_status = "Send to Pharmacy"

            has_items_to_add = True

        # Set the totals in the Pharmacy doc
        if has_items_to_add:
            pharmacy_doc.total_qty = total_qty
            pharmacy_doc.total_amount = total_amount

            # Save or update the Pharmacy doc as a draft
            pharmacy_doc.save(ignore_permissions=True)
            
            # Save changes to the original document
            doc.save(ignore_permissions=True)
            
            frappe.msgprint(_("Pharmacy Doc {0} created/updated successfully.").format(pharmacy_doc.name))
        # else:
        #     frappe.msgprint(_("No valid Prescriptions found"), raise_exception=False)

    except frappe.ValidationError as e:
        frappe.db.rollback()
        frappe.throw(_("There was an error creating the Pharmacy Doc: {0}").format(str(e)))

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(message=str(e), title="Pharmacy Doc Creation Error")
        frappe.throw(_("An unexpected error occurred while creating the Pharmacy Doc. Please try again or contact support. Error details: {0}").format(str(e)))


def ensure_treatment_is_included(doc, method):
    # Check if the drug_prescription field is set
    if doc.drug_prescription:
        # Check if "treatment" exists in the drug_prescription list
        treatment_included = any(item.medication == 'treatment' for item in doc.drug_prescription)
        
        # Throw an error if "treatment" is not found
        if not treatment_included:
            frappe.throw(_("Please include 'Treatment Fee' in the drug prescription for this patient."))

                
        