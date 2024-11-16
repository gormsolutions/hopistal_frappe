// Copyright (c) 2024, Paul Mututa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Test Statement', {
    refresh: function(frm) {
        // Add a custom button for fetching lab tests
        frm.add_custom_button(__('Fetch Lab Tests'), function() {
            fetch_lab_tests(frm);
        }).addClass('btn-primary');  // Add a CSS class to style the button
    },
    patient: function(frm) {
        fetch_lab_tests(frm);     
    }
});

// Function to fetch and process lab tests
function fetch_lab_tests(frm) {
    if (frm.doc.patient) {
        // Fetch patient lab test details from the backend
        frappe.call({
            method: "hmh_custom_app.custom_api.reports.latest_test.fetch_patient_labtest",  // Your backend method to fetch lab tests
            args: {
                patient: frm.doc.patient  // Assuming the 'patient' field is present in the form
            },
            callback: function(response) {
                if (response.message) {
                    let data = response.message;
                    console.log(data);

                    // Populate patient details in the form
                    frm.set_value('patient_name', data.patient_details.name);
                    frm.set_value('age', data.patient_details.age);
                    frm.set_value('sex', data.patient_details.sex);

                    // Clear existing child table (report_details)
                    frm.clear_table('report_details');

                    // Loop through the grouped lab test results by date
                    for (let date in data.lab_tests_grouped) {
                        let date_group = data.lab_tests_grouped[date];

                        // Loop through each test within that date
                        for (let test_key in date_group) {
                            let test_data = date_group[test_key];

                            // Process normal tests
                            test_data.normal_tests.forEach(function(test) {
                                let child_row = frm.add_child('report_details');
                                child_row.test_name = test.lab_test_name;
                                child_row.result_value = test.result_value;
                                child_row.lab_technician_name = test.employee_name;
                                child_row.doctor_name = test.practitioner_name;
                                child_row.date = date;
                                frm.refresh_field('report_details');
                            });

                            // Process descriptive tests
                            test_data.descriptive_tests.forEach(function(test) {
                                let child_row = frm.add_child('report_details');
                                child_row.test_name = test.lab_test_particulars;
                                child_row.result_value = test.result_value;
                                child_row.lab_technician_name = test.employee_name;
                                child_row.doctor_name = test.practitioner_name;
                                child_row.date = date;
                                frm.refresh_field('report_details');
                            });

                            // Process organism tests
                            test_data.organism_tests.forEach(function(test) {
                                let child_row = frm.add_child('report_details');
                                child_row.test_name = test.organism;
                                child_row.result_value = test.colony_population;
                                child_row.lab_technician_name = test.employee_name;
                                child_row.doctor_name = test.practitioner_name;
                                child_row.date = date;
                                frm.refresh_field('report_details');
                            });
                        }
                    }
                }
            }
        });
    } else {
        frappe.msgprint(__('Please select a patient first.'));
    }
}
