<?php


class JSSWebhook {
	
	
	private $Callbacks = [];
	
	/*
	* processHook will decode the Webhooks JSON to an array
	* and send it to an internal Method called 
	* evaluateCallbacks
	*/
	public function processHook($HookDetails)
	{
		$Details = json_decode($HookDetails, true);
		$this->evaluateCallbacks($Details);	
	}
	
	/*
	* evaluateCallbacks will loop through all stored Callbacks and detect
	* if the current Hook will match all triggers of a Callback.
	* At first all Base infos are evaluated - maybe we have a ComputerCheckIn
	* Callback defined only.
	*/
	private function evaluateCallbacks(array $Details)
	{
		// Loop through the Callbacks
		foreach($this->Callbacks as $Callback)
		{
			// Loop through their Base Definitions
			foreach($Callback["Details"]["webhook"] as $key => $value)
			{
				// Check if the defined Variables match
				if($Details["webhook"][$key] != $value)
				{
					// If they don't, try the Next Callback
					continue 2;
				}
				
			}
			// Loop through their Detail/Event Definitions
			foreach($Callback["Details"]["event"] as $key => $value)
			{
				// Check if the defined Variables match
				if($Details["event"][$key] != $value)
				{
					// If they don't, try the Next Callback
					continue 2;
				}
			}
			// All Requirements fullfilled, time to execute the Callback.
			$this->runCallback($Callback, $Details);
		}
		
	}
	
	/*
	* registerCallback will Register a Callback based on Object/Method/Detail Combination
	* of course only if the object and method exists.
	*/
	public function registerCallback($Object, $Method, $HookDetails)
	{
		// Check if the Object and Method exists
		if(is_object($Object) && method_exists($Object, $Method)) {
			// If yes, add the Callback
			$this->Callbacks[] = [
				"Object" => $Object,
				"Method" => $Method,
				"Details" => $HookDetails
			];
		}
	}
	
	/*
	* runCallback is the Method which will run the actual Callback.
	* After checking if the Object and Method still exists.
	*/
	private function runCallback($Callback, $Details)
	{
		// Check if the Object and Method exists
		if(is_object($Callback["Object"]) && method_exists($Callback["Object"], $Callback["Method"])) {
			// If yes, call the Callback.
			call_user_func([$Callback["Object"], $Callback["Method"]], $Details);
		}
	}
}

?>