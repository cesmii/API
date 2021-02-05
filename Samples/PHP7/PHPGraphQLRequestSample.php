<?php
require_once 'HTTP/Request2.php';

/* Dependencies to install via pear
 HTTP_Request2
*/

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

define('INSTANCE_GRAPHQL_ENDPOINT', 'https://YOURINSTANCE.cesmii.net/graphql');

/* You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
      But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
      expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
      you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). */
$current_bearer_token = "Value from Instance Portal -- You must include the prefix Bearer followed by a space";
// eg: Bearer eyJyb2xlIjoieW91cl9yb2xlIiwiZXhwIjoxNDk5OTk5OTk5LCJ1c2VyX25hbWUiOiJ5b3VydXNlcm5hbWUiLCJhdXRoZW50aWNhdG9yIjoieW91cmF1dGgiLCJhdXRoZW50aWNhdGlvbl9pZCI6Ijk5IiwiaWF0Ijo5OTk5OTk5OTk5LCJhdWQiOiJhdWQiLCJpc3MiOiJpc3MifQ==

/* These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
    Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
    credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
    In the Authenticator setup, you will also configure role, and Token expiry. */
define('CLIENT_ID', 'YourAuthenticatorName');
define('CLIENT_SECRET', 'YourAuthenticatorPassword');
define('USER_NAME', 'YourAuthenticatorBoundUserName');
define('ROLE', 'YourAuthenticatorRole');

//Call main program function
main();

//Forms and sends a GraphQL request (query or mutation) and returns the response
function perform_graphql_request($query, $endpoint, $bearertoken = "") {
    $query = str_replace(array("\r\n", "\r", "\n"), "", $query);    //cleanup strings
    $request = new HTTP_Request2();
    $request->setUrl($endpoint);
    $request->setMethod(HTTP_Request2::METHOD_POST);
    $headers = array(
        'Content-Type' => 'application/json'
    );
    if ($bearertoken != "") {
        $headers['Authorization'] = $bearertoken;
    }
    $request->setHeader($headers);
    $request->setBody($query);
    $response = $request->send();
    return $response->getBody();
    
    //TODO: Handle errors
}

//Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
function get_bearer_token() {

    // Step 1: Request a challenge
    $auth_response = perform_graphql_request("
        {\"query\":\" mutation {
            authenticationRequest(input:
            {authenticator:\\\"". CLIENT_ID . "\\\", 
                role: \\\"" . ROLE . "\\\", 
                userName: \\\"" . USER_NAME . "\\\"}) 
            { jwtRequest { challenge, message } } }
        \"}", INSTANCE_GRAPHQL_ENDPOINT);
    $auth_response = json_decode($auth_response);
    $challenge = $auth_response->data->authenticationRequest->jwtRequest->challenge;
    console_log ("Challenge is: " . $challenge);

    // Step 2: Get token
    $challenge_response = perform_graphql_request(
        "{\"query\":\" mutation {
            authenticationValidation(input:
                {authenticator:\\\"" . CLIENT_ID . "\\\", 
                signedChallenge: \\\"" . $challenge . "|" . CLIENT_SECRET . "\\\"})
            { jwtClaim } }
        \"}", INSTANCE_GRAPHQL_ENDPOINT);

    $challenge_response = json_decode($challenge_response);
    $new_jwt_token = $challenge_response->data->authenticationValidation->jwtClaim;
    return $new_jwt_token;

    //TODO: Handle errors!
}

//Main Program Function
function main() {
    console_log("Requesting Data from CESMII Smart Manufacturing Platform...");
    console_log();

    /* Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/wiki/GraphQL-Queries */
    $smp_query = "{\"query\":\"{
    query: equipments {
         id 
         displayName 
        }}
    \"}";        
    $smp_response = perform_graphql_request($smp_query, INSTANCE_GRAPHQL_ENDPOINT, $GLOBALS['current_bearer_token']);
    $smp_response = json_decode($smp_response);

    if (strpos(json_encode($smp_response), "expired") !== false)
    {
        console_log("Bearer Token expired!");
        console_log("Attempting to retreive a new GraphQL Bearer Token...");
        console_log();

        //Authenticate
        $new_token_response = get_bearer_token(INSTANCE_GRAPHQL_ENDPOINT);
        $GLOBALS['current_bearer_token'] = "Bearer " . $new_token_response;

        console_log("New Token received: " . $new_token_response . "<br/>");
        console_log();

        //Re-try our data request, using the updated bearer token
        //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
        $smp_response = perform_graphql_request($smp_query, INSTANCE_GRAPHQL_ENDPOINT, $GLOBALS['current_bearer_token']);
        $smp_response = json_decode($smp_response);
    }

    console_log("Response from SM Platform was... ");
    console_log(json_encode($smp_response, JSON_PRETTY_PRINT));
    console_log();
}

function console_log($line = "") {
    echo nl2br($line) . "<br/>";
}
?>