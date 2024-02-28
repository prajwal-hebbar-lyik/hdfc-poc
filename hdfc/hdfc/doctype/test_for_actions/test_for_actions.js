// Copyright (c) 2024, LYIK Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Test For Actions", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Test For Actions', {
  refresh: function(frm) {
    let button;
    if(frm.doc.status == "Approved") {
      button = "Approved";
    } else if (frm.doc.status == "Rejected") {
      button = "Rejected";
    } else {
      button = "ACTIONS"
    }
    frm.add_custom_button(__('Approve'), function() {
      frappe.confirm(
        'Are you sure to Approve?',
        function() {
          const value = frm.doc.name
          frappe.db.set_value('Test For Actions', value, {'status': 'Approved'});
          frappe.msgprint(`Record ${value} has been Approved`);
        },
        function() {
          // window.close();
        }
      );
    }, __(button));

    frm.add_custom_button(__('Reject'), function() {
      frappe.confirm(
        'Are you sure to Reject?',
        function() {
          const value = frm.doc.name
          frappe.db.set_value('Test For Actions', value, {'status': 'Rejected'});
          let d = new frappe.ui.Dialog({
            title: 'Reasons for Rejecting the Form',
            fields: [
                {
                    label: 'Reason',
                    fieldname: 'reason',
                    fieldtype: 'Text Editor'
                }
            ],
            size: 'small', // small, large, extra-large 
            primary_action_label: 'Submit',
            primary_action(values) {
                const value = frm.doc.name
                frappe.db.set_value('Test For Actions', value, {'reason': values.reason})
                d.hide();
            }
        });
        
        d.show();
          // frappe.msgprint(`Record ${value} has been rejected`);
        },
        function() {
          // window.close();
        }
      );
    }, __(button));

  }
})