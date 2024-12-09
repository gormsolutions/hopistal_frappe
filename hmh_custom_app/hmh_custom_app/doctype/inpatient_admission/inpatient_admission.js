// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Inpatient Admission", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Inpatient Admission', {
    wardroom_number: function(frm) {
        if (frm.doc.wardroom_number) {
            // Fetch the available beds linked to the selected room
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Beds',
                    filters: {
                        room: frm.doc.wardroom_number,  // Match room to the selected wardroom
                        status: 'Available'  // Filter beds that are available
                    },
                    fields: ['name']  // Get the bed names or IDs
                },
                callback: function(response) {
                    const beds = response.message || [];
                    if (beds.length > 0) {
                        // Populate the 'assigned_bed' field with available beds
                        // Setting the options for the Link field
                        let bed_options = beds.map(bed => bed.name);
                        
                        // Set the options for the assigned_bed field to show available beds
                        frm.fields_dict['assigned_bed'].get_query = function(doc, cdt, cdn) {
                            return {
                                filters: {
                                    'name': ['in', bed_options]  // Filter based on available beds
                                }
                            };
                        };
                        
                        frm.refresh_field('assigned_bed');
                    } else {
                        frappe.msgprint(__('No available beds for the selected wardroom.'));
                    }
                }
            });
        }
    }
});


