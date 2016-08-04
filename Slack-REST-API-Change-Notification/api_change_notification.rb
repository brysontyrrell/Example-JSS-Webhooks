#!/usr/bin/ruby

# This example uses the Sinatra micro-web-framework (http://www.sinatrarb.com/)
# to implement a simple web server for handling HTTP POST requests from the
# JSS WebHooks API. To install Sinatra, try 'sudo gem install sinatra'
#
# This example handles only the "RestAPIOPeration" event sent as JSON to the
# URL http://hostname.company.com:8000/rest_api_operation
#
# The handler for that URL parses the incoming JSON data about the event
# and constructs a message about it, which is then sent to a Slack channel via
# the "slacktee" command, available from https://github.com/course-hero/slacktee
#
# Be sure to set the SLACKTEE and SLACK_RECIPIENT constants as appropriate.
#
# Here's an example Slack message:
#
#    Casper user 'jeauxbleaux' just used the JSS API to create the
#    JSS Static Computer Group named 'Foobar' (id 14)
#
# To make it do something else with the message, change the last line of the
# `post '/rest_api_operation' do` block below.
#
# NOTE: For simplicity's sake, this example does NOT use a secure connection.
# If you don't trust the network between your JSS and the server running this,
# code (and you shouldn't) make sure to use a server with up-to-date SSL
# capabilities and be sure to use them. It is beyond the scope of this example
# to go into the many possibilities.
#
# To test this withouth a JSS, make this code executable, and run it.
# then in another terminal window on the same machine, use this curl command
#
#   curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST --data  '{"webhook":{"id":16,"name":"RestAPIOperationWebhook","webhookEvent":"RestAPIOperation"},"event":{"operationSuccessful":true,"objectID":1,"objectName":"Foobar","objectTypeName":"Static Computer Group","authorizedUsername":"jeauxbleaux","restAPIOperationType":"POST"}}'  http://localhost:8000/rest_api_operation
#
#

require 'sinatra/base'
require 'json'

# Set up a Sinatra web server to handle our hooks.
class WebHookHandler < Sinatra::Base

  ############ Constants ############

  SLACKTEE = "/usr/local/bin/slacktee"

  SLACK_RECIPIENT = "#jss-notify"

  ############ Sinatra configuration ############

  configure do
    set :bind, '0.0.0.0'
    set :port, 8000
    set :server, :webrick
  end # configure

  ############ Routes ############
  # Each of these handles an HTTP POST request to the
  # desired URL

  # https://servername.company.com:8000/rest_api_operation
  post '/rest_api_operation' do

    # the body is an IO stream, so ensure its at the start.
    request.body.rewind

    # Parse the JSON and extract the event data
    posted_json = JSON.parse(request.body.read, symbolize_names: true)
    event = posted_json[:event]

    # API operation types are GET, PUT, POST, and DELETE
    # Ignore GET operations, we only care about changes.
    action = case event[:restAPIOperationType]
             when "GET"
               return
             when "PUT"
               "update"
             when "POST"
               "create"
             when "DELETE"
               "delete"
             end

    # Use the event data to compose a message
    message = "Casper user '#{event[:authorizedUsername]}' just used the JSS API to #{action} the JSS #{event[:objectTypeName]} named '#{event[:objectName]}' (id #{event[:objectID]})"

    # send the message to the SLACK_RECEIPIENT via SLACKTEE
    system "echo \"#{message}\" | '#{SLACKTEE}' -p -c '#{SLACK_RECIPIENT}'"

  end # post '/rest_api_operation'

end # class

# Run the server
WebHookHandler.run!
