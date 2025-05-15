<?php
/**
 * M-PESA STK Push Implementation
 *
 * This script demonstrates how to implement the M-PESA STK Push functionality
 * using PHP. It handles both the access token retrieval and the STK push request.
 */

// Configuration
$config = [
    "BASE_URL" => "https://sandbox.safaricom.co.ke",
    "ACCESS_TOKEN_URL" => "/oauth/v1/generate?grant_type=client_credentials",
    "STK_PUSH_URL" => "/mpesa/stkpush/v1/processrequest",
    "BUSINESS_SHORT_CODE" => "174379",
    "PASSKEY" => "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
    "TILL_NUMBER" => "174379",
    "CALLBACK_URL" => "https://mydomain.com/path",
    "CONSUMER_KEY" => "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV",
    "CONSUMER_SECRET" => "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm",
];

/**
 * Get Access Token from M-PESA API
 *
 * @return string|null Access token or null if unsuccessful
 */
function getAccessToken() {
    global $config;

    $url = $config["BASE_URL"] . $config["ACCESS_TOKEN_URL"];
    $curl = curl_init();

    curl_setopt_array($curl, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => ["Content-Type: application/json"],
        CURLOPT_HTTPAUTH => CURLAUTH_BASIC,
        CURLOPT_USERPWD => $config["CONSUMER_KEY"] . ":" . $config["CONSUMER_SECRET"]
    ]);

    $response = curl_exec($curl);
    $error = curl_error($curl);

    curl_close($curl);

    if ($error) {
        echo "cURL Error: " . $error;
        return null;
    }

    $result = json_decode($response, true);

    // For debugging
    echo "Access Token Response: " . PHP_EOL;
    print_r($result);

    if (isset($result['access_token'])) {
        return $result['access_token'];
    }

    return null;
}

/**
 * Initiate STK Push Request
 *
 * @param int $amount Transaction amount
 * @param string $phoneNumber Customer phone number (format: 254XXXXXXXXX)
 * @return array Response from the STK push request
 */
function initiateSTKPush($amount = 1, $phoneNumber = "254463744444") {
    global $config;

    // Get access token
    $accessToken = getAccessToken();

    if (!$accessToken) {
        return ["error" => "Failed to get access token"];
    }

    // Generate timestamp and password
    $timestamp = date('YmdHis');
    $password = base64_encode($config["BUSINESS_SHORT_CODE"] . $config["PASSKEY"] . $timestamp);

    // Prepare STK Push request
    $url = $config["BASE_URL"] . $config["STK_PUSH_URL"];

    $stkPushPayload = [
        "BusinessShortCode" => $config["BUSINESS_SHORT_CODE"],
        "Password" => $password,
        "Timestamp" => $timestamp,
        "TransactionType" => "CustomerBuyGoodsOnline",
        "Amount" => $amount,
        "PartyA" => $phoneNumber,
        "PartyB" => $config["TILL_NUMBER"],
        "PhoneNumber" => $phoneNumber,
        "CallBackURL" => $config["CALLBACK_URL"],
        "AccountReference" => "DaSKF Raffle",
        "TransactionDesc" => "STK/IN Push"
    ];

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($stkPushPayload),
        CURLOPT_HTTPHEADER => [
            "Content-Type: application/json",
            "Authorization: Bearer " . $accessToken
        ]
    ]);

    $response = curl_exec($curl);
    $error = curl_error($curl);

    curl_close($curl);

    if ($error) {
        return ["error" => $error];
    }

    $result = json_decode($response, true);

    // For debugging
    echo "STK Push Response: " . PHP_EOL;
    print_r($result);

    return $result;
}

// Example usage
if (php_sapi_name() == 'cli') {
    // If running from command line
    echo "Initiating STK Push..." . PHP_EOL;
    $result = initiateSTKPush(1, "254712345678");
    echo "Result: " . PHP_EOL;
    print_r($result);
} else {
    // If being accessed via web
    header('Content-Type: application/json');

    // Get parameters from request
    $amount = isset($_REQUEST['amount']) ? (int)$_REQUEST['amount'] : 1;
    $phoneNumber = isset($_REQUEST['phone_number']) ? $_REQUEST['phone_number'] : "254463744444";

    $result = initiateSTKPush($amount, $phoneNumber);
    echo json_encode($result, JSON_PRETTY_PRINT);
}
?>
