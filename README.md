# Example-JSS-Webhooks
A collection of examples for using Webhooks with v9.93 of the JSS

Webhooks are outbound HTTP POST requests from a JSS containing a JSON or XML payload with data related to the event that was triggered. A webhook integration would run on a separate server from the JSS and receive these incoming requests to take action on.

This diagram is a basic overview of how these interactions work:

![Basic Webhoook Integration Diagram](/images/basic_webhook_integration_diagram.png)

Activity in the JSS (such as device check-ins shown above) will routinely trigger events in the Events API. If you have configured a webhook for one of these events it will send that event as JSON or XML to the URL you have specified.

At this point what your integration does with the data is up to you.

In the diagram you can see that the integration may perform calls to third party or external services *(directory services such as LDAP or OpenDirectory, chat apps like HipChat and Slack, or project management tools like JIRA and Trello)* and read or write to them over their APIs based upon the event or criteria the event matches that you have coded.

You can also have your integration take basic identifiers from the event *(e.g. event was triggered on an action of a computer or mobile device and contains the JSS ID / serial number / UUID)* and make return REST API calls to the JSS to modify the record or read in additional data before writing to another service *(e.g. real time integration to other management or inventory tools)*.


See [The Unofficial JSS API Docs: Webhooks API](https://unofficial-jss-api-docs.atlassian.net/wiki/display/JRA/Webhooks+API) for a full reference of all webhook events in both JSON and XML format.

# Email on Mobile Device Enroll and Un-Enroll

This is a webhooks version of a JSS Events API example demonstrated at the [2012 JNUC](https://www.youtube.com/watch?v=QGxMJ1r8_Lg) with the addition of listening for both **MobileDeviceEnrolled** and **MobileDeviceUnEnrolled** events.

When the event is received the integration parses the information for the mobile device and creates the email body in both plain text and HTML formats.

This email notification method can be adapted to any event within webhooks. Additional logic can be added to handle sending the alert to different email recipients depending upon the user assigned to the device. Another enhancement would be to tie into a directory service to look up the user's manager and then set the manager's email as the recipient and other required parties as CCs.


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

# Slack REST API Change Notification

This tiny Ruby example uses the [Sinatra micro-framework](http://www.sinatrarb.com/) to create a simple webserver to handle WebHook calls from the JSS. In particular, it handles the "RestAPIOperation" event as JSON,  but other handlers can be added easily. 

The JSON sent from the JSS is parsed for info about the API operation, ignoring any GET (read) operations, and then a message is built about the change that was made via the API.  The message is then sent to a slack channel or user via the "slacktee" command, available from [https://github.com/course-hero/slacktee](https://github.com/course-hero/slacktee). The message could also easily be sent via email or logged to a file. 

To use it, just make the script executable, and run it. Then create a webhook in the JSS sending RestAPIOperation events as JSON to http://hostname.company.com:8000/rest_api_operation where hostname.company.com is the host where the script is running. 

See the code comments for more details. Note: To install sinatra, try `sudo gem install sinatra`

# PHP Webhook Processing

If you want to have one Endpoint for all you Webhooks this may be the right solution for you. You'll just point the JSON-Body to JSSWebHook->processHook($JSON) and all Callbacks you registered before for this Webhook will be executed.

Please study the Code and the Usage.sample Code before you actually use this, it will be better explained inthere ;)

Filtering based on all Data within the Webhook request itself is possible, so you could just listen to any webhook containing your computer "Charly's iMac". The less filters you define the more webhook events you get.

This is free to use, edit, redistribute. But there may be bugs, you got the code, fix them yourself (and please report back).