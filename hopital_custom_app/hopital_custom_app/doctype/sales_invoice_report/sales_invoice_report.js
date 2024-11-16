// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Sales Invoice Report', {
//     customer: function(frm) {
//         let customer = frm.doc.customer;

//         if (customer) {
//             frappe.call({
//                 method: "hopital_custom_app.api.generate_customer_sales_summary",
//                 args: { customer: customer }
//             }).done((r) => {
//                 console.log(r)
//                 if (r.message && r.message.length > 0) {
//                     frm.doc.invoice_details = [];
//                     $.each(r.message, function(_i, invoice) {
//                         if (invoice.Items && invoice.Items.length > 0) {
//                             $.each(invoice.Items, function(_j, item) {
//                                 let entry = frappe.model.add_child(frm.doc, "Sales Invoice Details", "invoice_details");
//                                 entry.invoice = invoice.Invoice;
//                                 entry.outstanding_amount = invoice["Outstanding Amount"];
//                                 entry.grand_total = invoice["Grand Total"];
//                                 entry.posting_date = invoice["Posting Date"];
//                                 entry.patient_name = invoice["Patient Name"];
//                                 entry.item_code = item["Item Code"];
//                                 entry.qty = item.Qty;
//                                 entry.rate = item.Rate;
//                                 entry.amount = item.Amount;
//                                 // Add other fields as needed
//                             });
//                         }
//                     });
//                     frm.refresh_field("invoice_details");
//                     frappe.msgprint("Data inserted into the child table");
//                 } else {
//                     frappe.msgprint("No items to fetch");
//                 }
//             });
//         }
//     }
// });

