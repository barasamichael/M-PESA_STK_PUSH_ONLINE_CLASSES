const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

const config = {
    BASE_URL: "https://sandbox.safaricom.co.ke",
    ACCESS_TOKEN_URL: "/oauth/v1/generate?grant_type=client_credentials",
    STK_PUSH_URL: "/mpesa/stkpush/v1/processrequest",
    BUSINESS_SHORT_CODE: "174379",
    PASSKEY: "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
    TILL_NUMBER: "174379",
    CALLBACK_URL: "https://mydomain.com/path",
    CONSUMER_KEY: "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV",
    CONSUMER_SECRET: "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm",
};

/*
 * Get access token
 */
app.get('/get-access-token', async (req, res) => {
    const url = `${config.BASE_URL}${config.ACCESS_TOKEN_URL}`;
    try {
        const response = await axios.get(url, {
            auth: {
                username: config.CONSUMER_KEY,
                password: config.CONSUMER_SECRET
            },
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Comment this line in production
        console.log(response.data);

        res.json({
            access_token: response.data.access_token
        });
    } catch (error) {
        res.json({
            error: error.message
        });
    }
});

/*
 * Initiate STK Push
 */
app.post('/initiate-stk-push', async (req, res) => {
    const amount = req.body.amount || 1;
    const phoneNumber = req.body.phone_number || "254463744444";

    try {
        // Get access token
        const tokenUrl = `${config.BASE_URL}${config.ACCESS_TOKEN_URL}`;
        const tokenResponse = await axios.get(tokenUrl, {
            auth: {
                username: config.CONSUMER_KEY,
                password: config.CONSUMER_SECRET
            },
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const accessToken = tokenResponse.data.access_token;

        // Generate timestamp and password
        const timestamp = new Date().toISOString().replace(/[-T:.Z]/g, '').slice(0, 14);
        const password = Buffer.from(
            config.BUSINESS_SHORT_CODE + config.PASSKEY + timestamp
        ).toString('base64');

        // Prepare STK Push request
        const stkPushUrl = `${config.BASE_URL}${config.STK_PUSH_URL}`;
        const stkPushHeaders = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        };

        const stkPushPayload = {
            BusinessShortCode: config.BUSINESS_SHORT_CODE,
            Password: password,
            Timestamp: timestamp,
            TransactionType: "CustomerBuyGoodsOnline",
            Amount: amount,
            PartyA: phoneNumber,
            PartyB: config.TILL_NUMBER,
            PhoneNumber: phoneNumber,
            CallBackURL: config.CALLBACK_URL,
            AccountReference: "DaSKF Raffle",
            TransactionDesc: "STK/IN Push"
        };

        // Send STK Push request
        const stkPushResponse = await axios.post(
            stkPushUrl,
            stkPushPayload, {
                headers: stkPushHeaders
            }
        );

        console.log(stkPushResponse.data);
        res.json(stkPushResponse.data);

    } catch (error) {
        console.error(error);
        res.json({
            error: error.message
        });
    }
});

app.listen(3000, () => console.log('Server running on port 3000'));
