// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Pharmacy", {
//     refresh(frm) {
//         // You can add additional refresh logic here if needed
//     },
// });

frappe.ui.form.on('Pharmacy Items', {
    amount: function (frm, cdt, cdn) {
        calculateTotalsPharmacy(frm);
    },
    qty: function (frm, cdt, cdn) {
        calculateTotalsPharmacy(frm);
    },
    rate: function (frm, cdt, cdn) {
        calculateTotalsPharmacy(frm);
    },
    period: function(frm, cdt, cdn) {
        var item = frappe.get_doc(cdt, cdn);

        // Check if the period field has a value
        if (item.period) {
            if (frm.doc.price_list) {
                console.log("Price list found:", frm.doc.price_list);
                frappe.model.set_value(cdt, cdn, 'price_list', frm.doc.price_list);

                // Call the function to update the amount based on the item selected
                update_item_amount(frm, item, cdt, cdn);
            } else {
                console.log("No price list found.");
            }
        } else {
            console.log("Period is not selected.");
   
        }
    },
    dosage: function(frm, cdt, cdn) {
        var item = frappe.get_doc(cdt, cdn);

        // Check if the period field has a value
        if (item.period) {
            if (frm.doc.price_list) {
                console.log("Price list found:", frm.doc.price_list);
                frappe.model.set_value(cdt, cdn, 'price_list', frm.doc.price_list);

                // Call the function to update the amount based on the item selected
                update_item_amount(frm, item, cdt, cdn);
            } else {
                console.log("No price list found.");
            }
        } else {
            console.log("Period is not selected.");
   
        }
    }
});

function calculateTotalsPharmacy(frm) {
    var total_qty = 0;
    var total_amount = 0;

    frm.doc.drug_prescription.forEach(function (item) {
        // Calculate the amount for each item
        item.amount = item.qty * item.rate;
        total_qty += item.qty;
        total_amount += item.amount;
    });

    // Set the calculated totals in the form
    frm.set_value('total_qty', total_qty);
    frm.set_value('total_amount', total_amount);
    refresh_field('drug_prescription');
}


function update_item_amount(frm, item, cdt, cdn) {
    console.log("Calling server method to update amount...");
    frappe.call({
        method: 'hmh_custom_app.custom_api.drug_priscription.pharmacy_calculate',
        args: {
            pharmacy: frm.doc.name,
            selected_drug_code: item.drug_code, // Make sure to pass the selected drug code
            dosage: item.dosage,
            period: item.period,
        },
        callback: function(r) {
            console.log("Server response:", r);
            if (r.message) {
                var selected_item_amount = r.message.selected_item_amount;
                var qty = r.message.qty;
                var rate = r.message.rate;

                // Set the amount for the current drug_prescription item
                frappe.model.set_value(cdt, cdn, 'amount', selected_item_amount);
                frappe.model.set_value(cdt, cdn, 'qty', qty);
                frappe.model.set_value(cdt, cdn, 'rate', rate);

                // Optionally, you can also set the rate if needed
                frappe.model.set_value(cdt, cdn, 'rate', item.rate || 0);

        } else {
                frappe.msgprint(__('Error: ') + (r.message ? r.message.message : 'Unknown error'));
            }
        },
        error: function(r) {
            frappe.msgprint(__('Server call failed.'));
            console.error("Server call failed:", r);
        }
    });
}
