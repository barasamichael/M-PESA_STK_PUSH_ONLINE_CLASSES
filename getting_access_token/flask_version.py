import os
import requests

from flask import Flask
from flask import jsonify

app = Flask(__name__)


def getConfig():
    return {
        "BASE_URL": "https://sandbox.safaricom.co.ke",
        "ACCESS_TOKEN_URL": "oauth/v1/generate?grant_type=client_credentials",
        "CONSUMER_KEY": "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV",
        "CONSUMER_SECRET": "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm",
    }


@app.route("/get-access-token")
def get_access_token():
    """
    Sends a HTTP GET Request to retrieve a temporary access token.

    Notes:
        - When you move to production, change the `BASE_URL` to
          `https://api.safaricom.co.ke`.
        - Also change your `CONSUMER_KEY` AND `CONSUMER_SECRET` to match those
          provided to you by Safaricom.

    :return: None
    """
    config = getConfig()
    url = os.path.join(config["BASE_URL"], config["ACCESS_TOKEN_URL"])

    # Please take note that the Content-Type must always be JSON.
    headers = {"Content-Type": "application/json"}
    auth = (config["CONSUMER_KEY"], config["CONSUMER_SECRET"])

    try:
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        result = response.json()

        # Comment this line if you are not interested in viewing the json
        # result.
        print(result)

        return jsonify({"access_token": result["access_token"]})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
