<?php
    // Only execute if the incoming request is a POST
	if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Set a unique temprary file path for the incoming XML from the POST
		$tmp_path = '/tmp/comp' . time() . '.xml';

        // Get the XML data from the POST
		$data = file_get_contents('php://input');

        // Save the XML data at the temporary path
		file_put_contents($tmp_path, "$data");

        // Execute the script and pass the temporary file path as parameter 1
		shell_exec("./WebhookScript.sh " . $tmp_path);

        // Remove the temporary file
		unlink($tmp_path);
	}
?>