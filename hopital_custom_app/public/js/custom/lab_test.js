frappe.ui.form.on('Notify Doc', {
    onload: function(frm) {
        // Add custom button to set invoiced field
    
            frm.add_custom_button(__('Mark as Invoiced'), function() {
                frappe.call({
                    method: 'hopital_custom_app.custom.set_invoiced',
                    args: {
                        lab_test: frm.doc.name
                    },
                    callback: function(response) {
                        if (response.message) {
                            frappe.msgprint(__('Lab Test marked as invoiced'));
                            frm.reload_doc();
                        }
                    }
                });
            });
        
    }
});
