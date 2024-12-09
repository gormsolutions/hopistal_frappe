import frappe
from frappe import _
from frappe.model.document import Document

class InpatientAdmission(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_on_update_called = False  # Initialize a flag

    def on_update(self):
        # Prevent recursion by checking the flag
        if self._is_on_update_called:
            return

        # Set the flag to indicate that on_update has been called
        self._is_on_update_called = True

        # Initialize a variable to track if a status change occurred
        status_changed = False

        # Check the workflow state and update the admission_status accordingly
        if self.workflow_state == "Admission Scheduled":
            self.admission_status = "Admission Scheduled"
            status_changed = True

        elif self.workflow_state == "Admitted":
            # Check if rooms, beds, and admission reason are allocated
            if not self.wardroom_number or not self.assigned_bed or not self.admission_reason:
                frappe.throw(_("Please allocate a room, a bed, and provide an admission reason before admitting the patient."))

            # Check if the assigned bed is occupied
            bed_doc = frappe.get_doc("Beds", self.assigned_bed)
            if bed_doc.status == "Occupied" and bed_doc.room == self.wardroom_number:
                frappe.throw(_("The selected bed is already occupied. Please allocate a different bed."))

            # Check if the assigned room has available beds
            room_doc = frappe.get_doc("Rooms", self.wardroom_number)
            if room_doc.available_beds <= 0:
                frappe.throw(_("No available beds in the assigned room. Please allocate a different room."))

            # Update the admission_status
            self.admission_status = "Admitted"

            # Update the Room and Bed status
            self.update_room_and_bed("Occupied")
            status_changed = True

        elif self.workflow_state == "Under Treatment":
            self.admission_status = "Under Treatment"
            status_changed = True
            
            # Create a new Nursing Treatment document for the patient
            self.create_nurse_treatment_record()

        elif self.workflow_state == "Discharge Scheduled":
            self.admission_status = "Discharge Scheduled"
            status_changed = True

        elif self.workflow_state == "Discharged":
            self.admission_status = "Discharged"
            self.update_room_and_bed("Available")
            self.create_discharge_notes()
            status_changed = True

        # Save the document only if the admission_status has changed
        if status_changed or self.admission_status != self.get_old_value("admission_status"):
            self.save(ignore_permissions=True)

        # Reset the flag after update
        self._is_on_update_called = False

    def get_old_value(self, fieldname):
        """ Get the old value of a field before the current update. """
        return frappe.get_doc(self.doctype, self.name).get(fieldname)

    def update_room_and_bed(self, status):
        """ Update the status of the assigned room and bed. """
        room_doc = frappe.get_doc("Rooms", self.wardroom_number)
        bed_doc = frappe.get_doc("Beds", self.assigned_bed)

        # Update the status of room and bed custom_patient_id
        room_doc.status = status
        bed_doc.status = status

        # Update bed counts in the room
        if status == "Occupied":
            room_doc.occupied_beds += 1
            room_doc.available_beds -= 1
        elif status == "Available":
            room_doc.occupied_beds -= 1
            room_doc.available_beds += 1

        # Ensure bed counts don't go negative
        room_doc.occupied_beds = max(0, room_doc.occupied_beds)
        room_doc.available_beds = max(0, room_doc.available_beds)

        # Save the updates
        room_doc.save(ignore_permissions=True)
        bed_doc.save(ignore_permissions=True)

        # Optional: Additional notifications or logic can be handled here

    def create_discharge_notes(self):
        """Update the status of a Nurse Treatment Record for the inpatient to 'Discharge Scheduled'."""
    
        # Fetch the Nurse Treatment Record associated with this Inpatient Admission
        nurse_treatment_name = frappe.db.get_value("Nurse Treatment Record", 
                                               {"inpatient_admission": self.name}, 
                                               ["name"])
    
        if nurse_treatment_name:
            # Fetch the document using the name
            nurse_treatment_doc = frappe.get_doc("Nurse Treatment Record", nurse_treatment_name)
        
            # Update the status field to 'Discharge Scheduled'
            nurse_treatment_doc.record_status = "Discharged"
        
            # Save the updated document
            nurse_treatment_doc.save(ignore_permissions=True)
            frappe.msgprint(_("Nurse Treatment Record has been updated to 'Discharge'."))

        else:
            frappe.msgprint(_("No Nurse Treatment Record found for this admission."))

         
            
    def create_nurse_treatment_record(self):
        """Create or update a Nurse Treatment Record for the inpatient, including add, update, and delete operations."""
    
        # Fetch the Nurse Treatment Record associated with this Inpatient Admission
        nurse_treatment_name = frappe.db.get_value("Nurse Treatment Record", 
                                               {"inpatient_admission": self.name}, 
                                               ["name"])
    
        if nurse_treatment_name:
            # Fetch the existing Nurse Treatment Record
            nurse_treatment_doc = frappe.get_doc("Nurse Treatment Record", nurse_treatment_name)
            
            # Check if the status is 'Discharged', if so, don't proceed
            if nurse_treatment_doc.record_status == "Discharged":
                frappe.msgprint(_("Cannot proceed. The Nurse Treatment Record is already marked as 'Discharged'."))
                return  # Stop the function execution

            
            changes_made = False
        
            # Keep track of existing drug prescriptions to manage deletions
            existing_drug_codes = {t.drug_code for t in nurse_treatment_doc.doctors_prescription}

            # Handle Add or Update operations (Sync from Inpatient Admission to Nurse Treatment Record)
            for item in self.drug_prescription:
                # Check if the item already exists in Nurse Treatment Record
                existing_treatment_item = next((t for t in nurse_treatment_doc.doctors_prescription if t.drug_code == item.drug_code), None)
            
                if existing_treatment_item:
                    # Update fields if there are changes 
                    if (existing_treatment_item.date != item.date or
                        existing_treatment_item.time != item.time or
                        existing_treatment_item.number_of_repeats_allowed != item.number_of_repeats_allowed or
                        existing_treatment_item.dosage_form != item.dosage_form or
                        existing_treatment_item.dosage != item.dosage or
                        existing_treatment_item.strength_uom != item.strength_uom or
                        existing_treatment_item.period != item.period or
                        existing_treatment_item.comment != item.comment or
                        existing_treatment_item.drug_name != item.drug_name):
                    
                        # Update only the changed fields
                        existing_treatment_item.date = item.date
                        existing_treatment_item.time = item.time
                        existing_treatment_item.number_of_repeats_allowed = item.number_of_repeats_allowed
                        existing_treatment_item.dosage_form = item.dosage_form
                        existing_treatment_item.dosage = item.dosage
                        existing_treatment_item.strength_uom = item.strength_uom
                        existing_treatment_item.period = item.period
                        existing_treatment_item.comment = item.comment
                        existing_treatment_item.drug_name = item.drug_name
                        changes_made = True
                else:
                    # If not found, it's a new item, so append it
                    nurse_treatment_doc.append("doctors_prescription", {
                        "drug_code": item.drug_code,
                        "date": item.date,
                        "time": item.time,
                        "dosage_form": item.dosage_form,
                        "dosage": item.dosage,
                        "strength_uom": item.strength_uom,
                        "period": item.period,
                        "number_of_repeats_allowed": item.number_of_repeats_allowed,
                        "comment": item.comment,
                        "drug_name": item.drug_name,
                    })
                    changes_made = True

            # Handle Deletions (Remove items that no longer exist in Inpatient Admission) 
            new_drug_codes = {item.drug_code for item in self.drug_prescription}
            items_to_remove = [t for t in nurse_treatment_doc.doctors_prescription if t.drug_code not in new_drug_codes]

            if items_to_remove:
                for item in items_to_remove:
                    nurse_treatment_doc.remove(item)
                changes_made = True

            # Save changes if any updates or deletions were made
            if changes_made:
                nurse_treatment_doc.save(ignore_permissions=True)
                frappe.msgprint(_("Nurse Treatment Record has been updated based on Inpatient Admission changes."))
            else:
                frappe.msgprint(_("No changes found to update in Nurse Treatment Record."))

        # If Nurse Treatment Record does not exist, create a new one
        else:
            nurse_treatment_doc = frappe.get_doc({
                "doctype": "Nurse Treatment Record",
                "patient": self.patient_id,
                "inpatient_admission": self.name,
                "wardroom_number": self.wardroom_name,
                "bed_number": self.bed_no,
                "treatment_start_date": frappe.utils.now(),
                "record_status": "Ongoing"
            })

            # Add all items from the Inpatient Admission to the new Nurse Treatment Record
            for item in self.drug_prescription:
                nurse_treatment_doc.append("doctors_prescription", {
                    "drug_code": item.drug_code,
                    "date": item.date,
                    "time": item.time,
                    "dosage_form": item.dosage_form,
                    "dosage": item.dosage,
                    "strength_uom": item.strength_uom,
                    "number_of_repeats_allowed": item.number_of_repeats_allowed,
                    "period": item.period,
                    "comment": item.comment,
                    "drug_name": item.drug_name,
                })
        
            # Insert the new document into the database
            nurse_treatment_doc.insert(ignore_permissions=True)
            frappe.msgprint(_("Nurse Treatment Record has been created for the patient."))
