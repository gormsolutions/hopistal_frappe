app_name = "hopital_custom_app"
app_title = "Hopital Custom App"
app_publisher = "mututa paul"
app_description = "custom fiels and codes"
app_email = "mututapaul01@mail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hopital_custom_app/css/hopital_custom_app.css"
app_include_js = "/assets/hopital_custom_app/js/custom/lab_test.js"

# include js, css files in header of web template
# web_include_css = "/assets/hopital_custom_app/css/hopital_custom_app.css"
# web_include_js = "/assets/hopital_custom_app/js/hopital_custom_app.js"
# app_include_js = "assets/hopital_custom_app/js/custom/lab_test.js"
# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hopital_custom_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hopital_custom_app/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hopital_custom_app.utils.jinja_methods",
# 	"filters": "hopital_custom_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hopital_custom_app.install.before_install"
# after_install = "hopital_custom_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hopital_custom_app.uninstall.before_uninstall"
# after_uninstall = "hopital_custom_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hopital_custom_app.utils.before_app_install"
# after_app_install = "hopital_custom_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hopital_custom_app.utils.before_app_uninstall"
# after_app_uninstall = "hopital_custom_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hopital_custom_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# },
 
 "Sales Invoice": {
    "on_submit": [
        "hopital_custom_app.api.update_custom_procedure_invoiced",
        "hopital_custom_app.custom_field.create_journal_entry_on_sales_invoice_submit"
        
    ]
}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hopital_custom_app.tasks.all"
# 	],
# 	"daily": [
# 		"hopital_custom_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"hopital_custom_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hopital_custom_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hopital_custom_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hopital_custom_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hopital_custom_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hopital_custom_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hopital_custom_app.utils.before_request"]
# after_request = ["hopital_custom_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["hopital_custom_app.utils.before_job"]
# after_job = ["hopital_custom_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["module", "=", "Hopital Custom App"]
        ]
    },
    {
        "doctype": "Client Script",
        "filters": [
            ["module", "=", "Hopital Custom App"]
        ]
    },
]


# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hopital_custom_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

