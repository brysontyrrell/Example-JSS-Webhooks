# Example-JSS-Webhooks
A collection of examples for using Webhooks with v9.93 of the JSS

# Apache Script Runner

This is a very basic example of executing a shell script on every inbound request using Apache and PHP5.

In this basic example a POST sent to http://your.integration/script_runner.php will save the JSON or XML data to a temporary file, execute a script passing the filename as a parameter, the script reads the file and processes it (in this case the file contents are printed to a log file only) and then the temporary file is deleted.

While not as robust as an integration written using a web framework (see the Flask examples below) this is a quick and easy solution to trigger scripts upon events.

# HipChat JSS Upgrade Notification

This app listens for the JSSStartup event and notifies a chat room in HipChat when the JSS is reporting a newer version than during the last recorded startup.

A small database is used to track the version of the JSS. Some integrations you create will require local data stores to track changes over time. In this example I am using a library called SQLAlchemy for the interface to a SQL database.

In order to determine if a notification needs to be sent, the integration is going back out to the JSS to read the login page to obtain the version. An integration is able to perform multiple conditional actions on an inbound webhook to determine whether or not the automation should trigger. These can be local or external factors that require the integration to communicate with other services (not just the JSS).

# HipChat Patch Workflow Notification

This app is an example workflow automation. The integration notifies a HipChat room on every inbound PatchSoftwareTitleUpdated event. When the inbound patch title is "Firefox" that triggers additional actions to download the latest available version, notify the room when the download is complete, and then create a package ready for deployment to clients.

Consider similar workflows where an inbound event matching your criteria triggers automations with the integration or the integration triggers workflows in other services/apps.
