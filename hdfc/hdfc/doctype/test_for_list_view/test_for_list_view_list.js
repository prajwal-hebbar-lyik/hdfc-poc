frappe.listview_settings['Test For List View'] = {
    add_fields: ['Name', 'Date'],
    hide_name_column: true,
    hide_name_filter: true,
    onload(listview) {
        console.log("Hello ")
    }
}