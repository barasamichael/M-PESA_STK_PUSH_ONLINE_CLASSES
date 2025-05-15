<?php
$config = [
    "BASE_URL" => "https://sandbox.safaricom.co.ke",
    "ACCESS_TOKEN_URL" => "/oauth/v1/generate?grant_type=client_credentials",
    "CONSUMER_KEY" => "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV",
    "CONSUMER_SECRET" => "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm",
];

function getAccessToken($config) {
    $url = $config['BASE_URL'] . $config['ACCESS_TOKEN_URL'];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_USERPWD, $config['CONSUMER_KEY'] . ":" . $config['CONSUMER_SECRET']);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);

    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        echo json_encode(['error' => curl_error($ch)]);
    } else {
        $result = json_decode($response, true);
        echo json_encode(['access_token' => $result['access_token']]);
    }
    curl_close($ch);
}

getAccessToken($config);
?>
