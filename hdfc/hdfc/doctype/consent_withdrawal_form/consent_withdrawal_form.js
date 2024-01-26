// Copyright (c) 2024, LYIK Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Consent Withdrawal Form", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Consent Withdrawal Form', {
	refresh: function(frm) {
		//const full_name = frm.doc.full_name
		frm.add_custom_button(__('Approve'), function() {
			frappe.confirm(
				'Are you sure to Approve?',
				function() {
					//this will run on yes
					alert(frm.doc.cards);
				},
				function() {
					//this will run on no
					window.close();
				}
			);
	 	},__('ACTIONS'));
		frm.add_custom_button(__('Reject'), function() {
			frappe.confirm(
				'Are you sure to Reject?',
				function() {
					//this will run on yes
				},
				function() {
					//this will run  on no
					window.close();
				}
			);
		},__('ACTIONS'));
	}
});
