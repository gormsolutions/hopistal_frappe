// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient Payment Management', {
    patient: function(frm) {
        populateInvoiceTable(frm);
        populateInvoiceDetailedItemsDraftes(frm);
        populateInvoiceDetailedItems(frm)
    },
    update_totals:function(frm){
        calculateUpdateTotals(frm)
    },
    update_invoice_table:function(frm){
        populateInvoiceDetailedItems(frm)
    },
    update_drafts:function(frm){
        populateInvoiceDetailedItemsDraftes(frm);
    },
    sumbit_invoice:function(frm){
        submit_unique_invoices(frm);
    },
    on_submit: async function(frm) {
        // update_patient_bill_status(frm)
        const success = await submitPayments(frm);
        if (!success) {
            frappe.validated = false; // Prevent the form from saving
        } else {
            try {
                update_patient_bill_status(frm); // Call the function only if submitPayments is successful
            } catch (error) {
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('An error occurred while updating patient bill status.')
                });
            }
        }
    },
});

function populateInvoiceTable(frm) {
    // Clear the existing rows in the child table first
    frm.clear_table('invoice_details');
    frm.refresh_field('invoice_details');

    // Get the filters
    const cost_center = frm.doc.cost_center;
    const posting_date = frm.doc.posting_date;
    const patient = frm.doc.patient;

    if (patient) {
        // Call the server-side method
        frappe.call({
            method: 'hmh_custom_app.custom_api.sales_invoice.get_sales_invoices_with_totals',
            args: {
                cost_center: cost_center,
                posting_date: posting_date,
                patient: patient
            },
            callback: function(response) {
                // console.log(response)
                const invoices = response.message.Invoices;
                const totalOutstandingAmount = response.message['Total Outstanding Amount'];

                if (invoices && invoices.length > 0) {
                    // Add rows to the child table
                    invoices.forEach(invoice => {
                        let child = frm.add_child('invoice_details');
                        frappe.model.set_value(child.doctype, child.name, 'invoice', invoice.name);
                        frappe.model.set_value(child.doctype, child.name, 'outstanding_amount', invoice.outstanding_amount);
                        frappe.model.set_value(child.doctype, child.name, 'posting_date', invoice.posting_date);
                    });

                    // Refresh the child table
                    frm.refresh_field('invoice_details');

                    // Set the total outstanding amount
                    frm.set_value('total_outstandings', totalOutstandingAmount);
                } else {
                    // frappe.msgprint(__('No invoices found with the given filters.'));
                    frm.set_value('total_outstandings', 0);
                }
            },
            error: function(error) {
                // frappe.msgprint(__('An error occurred while fetching sales invoices.'));
                console.error(error);
            }
        });
    }
}


async function submitPayments(frm) {
    try {
        const response = await frappe.call({
            method: 'hmh_custom_app.custom_api.patient_payment.create_payments_mode',
            args: {
                patient_payment: frm.doc.name
            },
            freeze: true,
            freeze_message: __('Creating Payment Entries...')
        });

        if (response.message.error) {
            frappe.msgprint({
                title: __('Error'),
                indicator: 'red',
                message: response.message.error
            });
            return false;
        } else {
            frappe.msgprint({
                title: __('Success'),
                indicator: 'green',
                message: __('Payment Entries created successfully: {0}', [response.message.payment_entries.join(', ')])
            });
            return true;
        }
    } catch (error) {
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: __('An error occurred while creating payment entries.')
        });
        console.error(error);
        return false;
    }
}

function update_patient_bill_status(frm) {
    // Define the frappe.call requests sequentially to avoid the TimestampMismatchError
    frappe.call({
        method: 'hmh_custom_app.custom_api.update_labtest_status.update_lab_tests_payment_status',
        args: {
            'custom_payment_id': frm.doc.patient
        }
    }).then((labTestResponse) => {
        if (labTestResponse.message) {
            frappe.msgprint(labTestResponse.message);
        }

        return frappe.call({
            method: 'hmh_custom_app.custom_api.radiology.update_radiology_status.update_rediology_payment_status',
            args: {
                'custom_payment_id': frm.doc.patient
            }
        });
    }).then((radiologyResponse) => {
        if (radiologyResponse.message) {
            frappe.msgprint(radiologyResponse.message);
        }

        return frappe.call({
            method: 'hmh_custom_app.custom_api.procedures.update_procedure_status.update_procedure_payment_status',
            args: {
                'custom_payment_id': frm.doc.patient
            }
        });
    }).then((procedureResponse) => {
        if (procedureResponse.message) {
            frappe.msgprint(procedureResponse.message);
        }

        return frappe.call({
            method: 'hmh_custom_app.custom_api.patient.update_patient_bill_status',
            args: {
                'custom_payment_id': frm.doc.patient
            }
        });
    }).then((patientResponse) => {
        if (patientResponse.message) {
            frappe.msgprint(patientResponse.message);
        }

        return frappe.call({
            method: 'hmh_custom_app.pharmacy_jouney.approved_invoice.pharmacy_status',
            args: {
                'custom_payment_id': frm.doc.patient
            }
        });
    }).then((pharmacyResponse) => {
        if (pharmacyResponse.message) {
            frappe.msgprint(pharmacyResponse.message);
        }
    }).catch((error) => {
        frappe.msgprint(__('An error occurred while updating the statuses.'));
        console.error(error);
    });
}


function populateInvoiceTableDraftes(frm) {
    // Clear the existing rows in the child table first
    frm.clear_table('invoice_awaiting');
    frm.refresh_field('invoice_awaiting');

    // Get the filters
    const cost_center = frm.doc.cost_center;
    const posting_date = frm.doc.posting_date;
    const patient = frm.doc.patient;

    if (patient) {
        // Call the server-side method
        frappe.call({
            method: 'hmh_custom_app.custom_api.sales_invoice.get_sales_invoices_with_drafts_itemgroup',
            args: {
                cost_center: cost_center,
                posting_date: posting_date,
                patient: patient
            },
            callback: function(response) {
                // console.log(response)
                const invoices = response.message.Invoices;
                if (invoices && invoices.length > 0) {
                    // Add rows to the child table
                    invoices.forEach(invoice => {
                        let child = frm.add_child('invoice_awaiting');
                        frappe.model.set_value(child.doctype, child.name, 'invoice', invoice.name);
                        frappe.model.set_value(child.doctype, child.name, 'outstanding_amount', invoice.outstanding_amount);
                        frappe.model.set_value(child.doctype, child.name, 'posting_date', invoice.posting_date);
                    });

                    // Refresh the child table
                    frm.refresh_field('invoice_awaiting');
                } else {
                    // frappe.msgprint(__('No invoices found with the given filters.'));
                }
            },
            error: function(error) {
                // frappe.msgprint(__('An error occurred while fetching sales invoices.'));
                console.error(error);
            }
        });
    }
}

frappe.ui.form.on('Modes of Payment Items', {
    paid_amount: function (frm, cdt, cdn) {
        calculateTotalsPayment(frm);
    },

});

function calculateTotalsPayment(frm) {
    frm.set_value('total_paid_amount', "");
    var total_amount = 0;
    frm.doc.cash_items.forEach(function (item) {
        total_amount += item.paid_amount;
       });
    frm.set_value('total_paid_amount', total_amount);
    refresh_field('cash_items');
}


function populateInvoiceDetailedItems(frm) {
    // Clear the existing rows in the child table first
    frm.clear_table('invoice_detailed_items');
    frm.refresh_field('invoice_detailed_items');

    // Get the filters
    const cost_center = frm.doc.cost_center;
    const posting_date = frm.doc.posting_date;
    const patient = frm.doc.patient;

    if (patient) {
        // Call the server-side method
        frappe.call({
            method: 'hmh_custom_app.custom_api.sales_invoice.get_sales_invoices_with_totals_itemgroup',
            args: {
                cost_center: cost_center,
                posting_date: posting_date,
                patient: patient
            },
            callback: function(response) {
                // console.log(response)
                const item_codes = response.message['Item Group Totals'];
                const totalOutstandingAmount = response.message['Total Outstanding Amount'];

                if (item_codes && item_codes.length > 0) {
                    // Add rows to the child table 
                    item_codes.forEach(item => {
                        let child = frm.add_child('invoice_detailed_items');
                        frappe.model.set_value(child.doctype, child.name, 'item', item.item_code);
                        frappe.model.set_value(child.doctype, child.name, 'self_request', item.self_request);
                        frappe.model.set_value(child.doctype, child.name, 'invoice', item.invoice_name);
                        frappe.model.set_value(child.doctype, child.name, 'outstanding_amount', item.total_amount);
                       
                    });

                    // Refresh the child table
                    frm.refresh_field('invoice_detailed_items');

                    // Set the total outstanding amount
                    frm.set_value('totals', totalOutstandingAmount);
                } else {
                    // frappe.msgprint(__('No invoices found with the given filters.'));
                    frm.set_value('total_outstandings', 0);
                }
            },
            error: function(error) {
                // frappe.msgprint(__('An error occurred while fetching sales invoices.'));
                console.error(error);
            }
        });
    }
}



function calculateUpdateTotals(frm) {
    frm.set_value('totals', "");
    var total_amount = 0;
    frm.doc.invoice_detailed_items.forEach(function (item) {
        total_amount += item.outstanding_amount;
       });
    frm.set_value('totals', total_amount);
    refresh_field('invoice_detailed_items');
}

function populateInvoiceDetailedItemsDraftes(frm) {
    // Clear the existing rows in the child table first
    frm.clear_table('invoice_awaiting');
    frm.refresh_field('invoice_awaiting');

    // Get the filters
    const cost_center = frm.doc.cost_center;
    const posting_date = frm.doc.posting_date;
    const patient = frm.doc.patient;

    if (patient) {
        // Call the server-side method
        frappe.call({
            method: 'hmh_custom_app.custom_api.sales_invoice.get_sales_invoices_with_drafts_itemgroup',
            args: {
                cost_center: cost_center,
                posting_date: posting_date,
                patient: patient
            },
            callback: function(response) {
                // console.log(response);
                const invoices = response.message.Invoices;
                const item_group = response.message['Item Group Totals'];

                if (item_group && item_group.length > 0) {
                    // Add rows to the child table
                    item_group.forEach(item => {
                        let child = frm.add_child('invoice_awaiting');
                        frappe.model.set_value(child.doctype, child.name, 'invoice', item.invoice_ids.join(', '));
                        frappe.model.set_value(child.doctype, child.name, 'item', item.item_code);
                        frappe.model.set_value(child.doctype, child.name, 'outstanding_amount', item.total_amount);
                    });

                    // Refresh the child table
                    frm.refresh_field('invoice_awaiting');
                } else {
                    // frappe.msgprint(__('No item group totals found with the given filters.'));
                }
            },
            error: function(error) {
                // frappe.msgprint(__('An error occurred while fetching sales invoices.'));
                console.error(error);
            }
        });
    } else {
        frappe.msgprint(__('Please select a patient.'));
    }
}

// Function to submit the Sales Invoice

function submit_unique_invoices(frm) {
    frappe.call({
        method: 'hmh_custom_app.custom_api.submit_doc.submit_unique_invoices',
        args: {
            parent_docname: frm.doc.name
        },
        callback: function(response) {
            if (response.message.status === 'error') {
                frappe.msgprint(__('Error: {0}', [response.message.message]));
            } else {
                let successMsg = __('Successfully submitted invoices: {0}', [response.message.submitted_invoices.join(', ')]);
                if (response.message.failed_invoices.length > 0) {
                    successMsg += '<br>' + __('Failed to submit invoices: {0}', [response.message.failed_invoices.join(', ')]);
                }
                frappe.msgprint(successMsg);
                frm.reload_doc(); // Reload the form to reflect changes
            }
        },
        error: function(err) {
            // frappe.msgprint(__('An error occurred while submitting invoices.'));
            console.error(err);
        }
    });
}

