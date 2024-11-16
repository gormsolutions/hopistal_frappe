import frappe
from frappe import _
from frappe.utils import add_days

@frappe.whitelist()
def create_journal_entry_on_sales_invoice_submit(doc, method):
    # Check if the "patient" field is set in the Sales Invoice document
    if not doc.get("patient"):
        return

    # Retrieve the Sales Invoice document by its name
    sales_invoice = frappe.get_doc("Sales Invoice", doc.name)
  
    # Check if the customer is assigned to the "Employee" customer group
    customer_group = frappe.get_value("Customer", sales_invoice.customer, "customer_group")
    if customer_group != "Employee":
        return
    
    # Get the custom_employee field from the Customer document
    employee_id = frappe.get_value("Customer", sales_invoice.customer, "custom_employee")
    
    if not employee_id:
        frappe.msgprint(_("Custom Employee field is not set for this customer."))
        return

    posting_date = sales_invoice.posting_date
    repayment_start_date = add_days(posting_date, 10)

    # Create Journal Entry for staff medical bills payable
    journal_entry = frappe.get_doc({
        "doctype": "Journal Entry",
        "posting_date": posting_date,
        "accounts": [
            {
                "account": "3120-8 - Staff Medical Bills Payable - KH",
                "party_type": "Employee",
                "party": employee_id,
                "debit_in_account_currency": sales_invoice.grand_total 
            },
            {
                "account": "1100-7 - Staff Medical Debtors - KH",
                "party_type": "Customer",
                "party": sales_invoice.customer,
                "credit_in_account_currency": sales_invoice.grand_total,
                "reference_type": "Sales Invoice",
                "reference_name": doc.name
            }
        ]
    })

    # Save and submit the Journal Entry
    journal_entry.insert(ignore_permissions=True)
    journal_entry.submit()

    # Create Loan Application
    loan_application = frappe.get_doc({
        "doctype": "Loan",
        "applicant": employee_id,
        "applicant_type": "Employee",
        "repay_from_salary": 1,
        "loan_product": "Staff Medical Employee Debtors",
        "repayment_method": "Repay Fixed Amount per Period",
        "repayment_start_date": repayment_start_date,
        "posting_date": posting_date,
        "monthly_repayment_amount": sales_invoice.grand_total,
        "loan_amount": sales_invoice.grand_total,
        "custom_voucher_no": sales_invoice,
        "custom_patient_name": sales_invoice.patient_name,
        "remarks": _("Loan Application created from Sales Invoice {0}").format(doc.name)
    })
    loan_application.insert(ignore_permissions=True)

    # If the loan amount is below 50000, submit the Loan Application
    if loan_application.loan_amount < 50000:
        loan_application.submit()
        frappe.msgprint(_("Journal Entry and Loan created and submitted successfully."))
    else:
        frappe.msgprint(_("Journal Entry and Loan created. Loan amount exceeds 50000 and has been saved as draft.Contact HR for clarification"))
