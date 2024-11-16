import frappe
from frappe.model.document import Document

@frappe.whitelist()
def create_stock_entry(docname, warehouse, posting_date, posting_time, patient, cost_center):
    # Check if Stock Entry already exists
    stock_entry_list = frappe.get_list('Stock Entry', filters={'custom_pharmacy_id': docname, 'docstatus': 1}, fields=['name'])
    
    if stock_entry_list:
        return {'status': 'exists', 'message': 'Items already Issued Please'}
    
    # Fetch the Pharmacy document
    pharmacy = frappe.get_doc('Pharmacy', docname)
    
    if not pharmacy:
        return {'status': 'error', 'message': 'Pharmacy document not found'}
    
    # Create new Stock Entry
    se = frappe.new_doc('Stock Entry')
    se.stock_entry_type = 'Material Issue'
    se.remarks = f"{patient} - {docname}"
    se.posting_date = posting_date
    se.posting_time = posting_time
    se.custom_patient_id = patient
    se.custom_pharmacy_id = docname
    
    # Check if negative stock is allowed
    allow_negative_stock = frappe.db.get_single_value('Stock Settings', 'allow_negative_stock')
    
    # Add Stock Entry details based on Medication Entry items
    for item in pharmacy.drug_prescription:
        item_code = item.drug_code
        item_doc = frappe.get_doc('Item', item_code)
        uom = item_doc.stock_uom  # Retrieve the UOM from the Item document
        
        # Check if the item has batch tracking enabled
        has_batch = frappe.get_value('Item', item_code, 'has_batch_no')
        
        if has_batch:
            # Get the batch with the highest available quantity
            batch_info = frappe.get_list('Batch', filters={
                'item': item_code
            }, fields=['batch_id', 'batch_qty'], order_by='batch_qty desc', limit=1)  # Get the batch with the most stock
            
            if batch_info:
                batch_no = batch_info[0]['batch_id']
            else:
                batch_no = None  # No available batch found
        else:
            batch_no = None  # No batch tracking for this item

        se.append('items', {
            'item_code': item_code,
            'qty': item.qty,
            'uom': uom,
            's_warehouse': warehouse,
            'transfer_qty': item.qty,
            'cost_center': cost_center,
            'use_serial_batch_fields': 1,
            'batch_no': batch_no  # Set the batch number if available
        })
    
    if allow_negative_stock:
        frappe.db.set_value('Stock Entry', se.name, 'allow_negative_stock', 1)  # Ensure negative stock is allowed for this Stock Entry

    se.insert()
    se.submit()
    
    return {'status': 'created', 'name': se.name}
