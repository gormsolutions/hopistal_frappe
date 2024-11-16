// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Collect Patient Payment", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Collect Patient Payment', {
    refresh: function(frm) {
        if (frm.doc.discount == 0) {
            // Show the discount_account field
            frm.toggle_display('discount_account', false);}
        // Function to create sales invoice
        function createSalesInvoice() {
            frappe.call({
                method: "hmh_custom_app.custom_api.sales_invoice.create_sales_invoice",
                args: {
                    patient_payment: frm.doc.name
                },
                callback: function(response) {
                    if (response.message) {
                        frappe.msgprint(response.message);
                    } else if (response.error) {
                        frappe.msgprint(__('Error: ') + response.error);
                    } else {
                        frappe.msgprint(__('Failed to create Sales Invoice.'));
                    }
                },
                error: function(error) {
                    frappe.msgprint(__('There was an error creating the Sales Invoice.'));
                    console.error(error);
                }
            });
        }
        function createSalesInvoicePayments() {
            frappe.call({
                method: "hmh_custom_app.custom_api.sales_invoice.create_sales_invoice_payments",
                args: {
                    patient_payment: frm.doc.name
                },
                callback: function(response) {
                    if (response.message) {
                        frappe.msgprint(response.message);
                    } else if (response.error) {
                        frappe.msgprint(__('Error: ') + response.error);
                    } else {
                        frappe.msgprint(__('Failed to create Sales Invoice.'));
                    }
                },
                error: function(error) {
                    frappe.msgprint(__('There was an error creating the Sales Invoice.'));
                    console.error(error);
                }
            });
        }

// Show/hide "Bill Now" or "Bill Later" button based on customer_group and bill_status fields
function toggleBillButton() {
    var showBillNow = true;

    // Determine if "Bill Now" should be shown
    if (frm.doc.customer_group === "Insurance" || frm.doc.bill_status === "CLOSED") {
        showBillNow = false;
    }

    // Clear previous actions
    frm.page.clear_actions_menu();

    // Set button actions and visibility based on bill_status
    if (frm.doc.bill_status !== "CLOSED") {
        if (showBillNow) {
            frm.page.set_primary_action(__('Bill Now'), function() {
                createSalesInvoicePayments();
            }, 'bill_now_button');
        } else {
            frm.page.set_primary_action(__('Bill Later'), function() {
                createSalesInvoice();
            }, 'bill_later_button');
        }
       
        // Toggle display based on showBillNow
        frm.toggle_display(['bill_now_button'], showBillNow);
        frm.toggle_display(['bill_later_button'], !showBillNow);
    } else {
        // Hide both buttons if bill_status is "CLOSED"
        frm.toggle_display(['bill_now_button', 'bill_later_button'], false);
    }
}


        // Call toggleBillButton on form load and on customer_group or bill_status field change
        toggleBillButton();
        frm.fields_dict.customer_group.$input.on('change', function() {
            toggleBillButton();
        });
        frm.fields_dict.bill_status.$input.on('change', function() {
            toggleBillButton();
        });
    },
    discount: function(frm) {
        // Check if the discount amount is greater than 0
        if (frm.doc.discount > 0) {
            // Show the discount_account field
            frm.toggle_display('discount_account', true);
            
            // Prompt the user to enter the discount account if it's not already set
            if (!frm.doc.discount_account) {
                frappe.prompt(
                    {
                        label: 'Discount Account',
                        fieldname: 'discount_account',
                        fieldtype: 'Link',
                        options: 'Account',
                        default:'5755 - Discount Allowed - HMH',
                        reqd: 1
                    },
                    function(values) {
                        // Set the discount_account field with the selected value
                        frm.set_value('discount_account', values.discount_account);
                    },
                    'Enter Discount Account If not the one set',
                    'OK'
                );
            }
        } else {
            // Hide the discount_account field if discount is 0 or less
            frm.toggle_display('discount_account', false);
        }
    },
    posting_date: function (frm) {
        // Calculate the due date as posting date + 30 days
        var postingDate = new Date(frm.doc.posting_date);
        var dueDate = new Date(postingDate.setDate(postingDate.getDate() + 30));

        // Format due date as YYYY-MM-DD
        var formattedDueDate = dueDate.toISOString().split('T')[0];

        // Set the due date in the form
        frm.set_value('due_date', formattedDueDate);
    },
});


frappe.ui.form.on('Payment Items', {
    amount: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    },
    qty: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    },
    rate: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    },

    item_code: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
        fetch_price(frm);
    }
});

frappe.ui.form.on('Modes of Payment Items', {
    paid_amount: function (frm, cdt, cdn) {
        calculateTotalsPayment(frm);
    },

});

function calculateTotalsTransfers(frm) {
    frm.set_value('grand_totals', "");
    frm.set_value('total_qty', "");
    var total_amount = 0;
    var total_qty = 0;
    frm.doc.items.forEach(function (item) {
        item.amount = item.rate * item.qty;
        total_amount += item.amount;
        total_qty += item.qty;
    });
    frm.set_value('grand_totals', total_amount);
    frm.set_value('total_qty', total_qty);
    refresh_field('items');
}

function fetch_price(frm) {
    frm.doc.items.forEach(function (item) {
        frappe.call({
            method: "hmh_custom_app.custom_api.fetch_item_price.fetch_item_rate",
            args: {
                item_code: item.item_code,
                price_list: frm.doc.price_list
            },
            callback: function(response) {
                if (response.message) {
                    frappe.model.set_value(item.doctype, item.name, 'rate', response.message);
                }
            }
        });
    });
}

function calculateTotalsPayment(frm) {
    frm.set_value('total_paid_amount', "");
    var total_amount = 0;
    frm.doc.cash_items.forEach(function (item) {
        total_amount += item.paid_amount;
       });
    frm.set_value('total_paid_amount', total_amount);
    refresh_field('cash_items');
}




