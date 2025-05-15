import os
import base64
import requests
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)


def getConfig():
    return {
        "BASE_URL": "https://sandbox.safaricom.co.ke",
        "ACCESS_TOKEN_URL": "oauth/v1/generate?grant_type=client_credentials",
        "STK_PUSH_URL": "mpesa/stkpush/v1/processrequest",
        "STK_QUERY_URL": "mpesa/stkpushquery/v1/query",
        "BUSINESS_SHORT_CODE": "174379",
        "PASSKEY": "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
        "TILL_NUMBER": "174379",
        "CALLBACK_URL": "https://mydomain.com/path",
        "CONSUMER_KEY": "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV",
        "CONSUMER_SECRET": "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm",
    }


@app.route("/get-access-token")
def get_access_token():
    """
    Sends a HTTP GET Request to retrieve a temporary access token.

    :return: JsonResponse with access token or error
    """
    config = getConfig()
    url = os.path.join(config["BASE_URL"], config["ACCESS_TOKEN_URL"])
    headers = {"Content-Type": "application/json"}
    auth = (config["CONSUMER_KEY"], config["CONSUMER_SECRET"])

    try:
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        result = response.json()
        return jsonify({"access_token": result["access_token"]})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})


@app.route("/initiate-stk-push", methods=["POST"])
def initiate_stk_push():
    """
    Initiates an STK push

    Expected JSON payload:
    {
        "amount": 1,
        "phone_number": "254XXXXXXXXX"
    }

    :return: JsonResponse with STK push result or error
    """
    data = request.get_json()
    amount = data.get("amount", 1)
    phone_number = data.get("phone_number", "254463744444")

    config = getConfig()

    # Get access token
    token_response = get_access_token()
    token_data = token_response.get_json()

    if "error" in token_data:
        return jsonify({"error": "Failed to get access token"})

    access_token = token_data["access_token"]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (config["BUSINESS_SHORT_CODE"] + config["PASSKEY"] + timestamp).encode()
    ).decode()

    query_url = os.path.join(config["BASE_URL"], config["STK_PUSH_URL"])

    stk_push_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    stk_push_payload = {
        "BusinessShortCode": config["BUSINESS_SHORT_CODE"],
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": config["TILL_NUMBER"],
        "PhoneNumber": phone_number,
        "CallBackURL": config["CALLBACK_URL"],
        "AccountReference": "DaSKF Raffle",
        "TransactionDesc": "STK/IN Push",
    }

    try:
        response = requests.post(
            query_url, headers=stk_push_headers, json=stk_push_payload
        )
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})


@app.route("/query-stk-status", methods=["POST"])
def query_stk_status():
    """
    Queries the status of an STK push transaction

    Expected JSON payload:
    {
        "checkout_request_id": "ws_CO_DMZ_12345678901234567"
    }

    :return: JsonResponse with STK query result or error
    """
    data = request.get_json()
    checkout_request_id = data.get("checkout_request_id")

    if not checkout_request_id:
        return jsonify({"error": "Checkout Request ID not provided"})

    config = getConfig()

    # Get access token
    token_response = get_access_token()
    token_data = token_response.get_json()

    if "error" in token_data:
        return jsonify({"error": "Failed to get access token"})

    access_token = token_data["access_token"]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (config["BUSINESS_SHORT_CODE"] + config["PASSKEY"] + timestamp).encode()
    ).decode()

    query_url = os.path.join(config["BASE_URL"], config["STK_QUERY_URL"])

    query_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    query_payload = {
        "BusinessShortCode": config["BUSINESS_SHORT_CODE"],
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }

    try:
        response = requests.post(
            query_url, headers=query_headers, json=query_payload
        )
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
