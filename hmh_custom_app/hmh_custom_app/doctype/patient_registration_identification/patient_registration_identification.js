// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt
// frappe.ui.form.on("Patient Registration Identification", {
//     onload: function(frm) {
//         // Ensure the custom phone field is initialized with Uganda code
//         if (!frm.doc.patient_phone || !frm.doc.patient_phone.startsWith('+256')) {
//             frm.set_value('patient_phone', '+256');
//         }
//     }
// });

frappe.ui.form.on('Patient Registration Identification', {
    customer_group: function(frm) {
        // Clear the customer field
        frm.set_value('customer', '');
        
        // Set the filter for the customer field based on the selected customer group
        if (frm.doc.customer_group) {
            frm.set_query('customer', function() {
                return {
                    filters: {
                        'customer_group': frm.doc.customer_group
                    }
                };
            });
        } else {
            frm.set_query('customer', function() {
                return {
                    filters: {}
                };
            });
        }
    },

    date_of_birth: function(frm) {
        if (frm.doc.date_of_birth) {
            const dob = new Date(frm.doc.date_of_birth);
            const today = new Date();
            
            // Calculate the full age in years
            let ageYears = today.getFullYear() - dob.getFullYear();
            let ageMonths = today.getMonth() - dob.getMonth();
            let ageDays = today.getDate() - dob.getDate();

            if (ageDays < 0) {
                ageMonths--;
                ageDays += new Date(today.getFullYear(), today.getMonth(), 0).getDate();
            }

            if (ageMonths < 0) {
                ageYears--;
                ageMonths += 12;
            }

            // Ensure age is not negative
            ageYears = Math.max(ageYears, 0);
            ageMonths = Math.max(ageMonths, 0);
            ageDays = Math.max(ageDays, 0);

            // Format the age summary
            const ageSummary = `${ageYears} years, ${ageMonths} months, ${ageDays} days`;

            // Set the age summary
            frm.set_value('age_summary', ageSummary);
            frm.set_value('full_age', ageYears);
        } else {
            frm.set_value('age_summary', null);
            frm.set_value('full_age', null);
        }
    }
});

