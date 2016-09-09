<?php
// this is how to use the JSSWebhook Class
require_once "JSSWebhook.php";
$JSSWH = new JSSWebhook();
class test {
	
	public function __construct()
	{
		global $JSSWH;
		$JSSWH->registerCallback($this, "test", [
			"webhook" => [
			], 
			"event" => [
			]
		]);
	}
	public function test($Details)
	{
		var_dump($Details);
	}
}
new test();
$JSSWH->processHook('{
  "webhook": {
    "id": 1,
    "name": "ComputerAdded Webhook",
    "webhookEvent": "ComputerAdded"
  },
  "event": {
    "udid": "",
    "deviceName": "",
    "model": "",
    "macAddress": "",
    "alternateMacAddress": "",
    "serialNumber": "",
    "osVersion": "",
    "osBuild": "",
    "userDirectoryID": "-1",
    "username": "",
    "realName": "",
    "emailAddress": "",
    "phone": "",
    "position": "",
    "department": "",
    "building": "",
    "room": "",
    "jssID": 1
  }
}');

?>