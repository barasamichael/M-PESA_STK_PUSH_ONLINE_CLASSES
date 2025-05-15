const express = require('express');
const axios = require('axios');
const app = express();

const config = {
    BASE_URL: "https://sandbox.safaricom.co.ke",
    ACCESS_TOKEN_URL: "/oauth/v1/generate?grant_type=client_credentials",
    CONSUMER_KEY: "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV",
    CONSUMER_SECRET: "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm",
};

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

        /*
         * Do not display this line in production. Comment it if need be.
         */
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

app.listen(3000, () => console.log('Server running on port 3000'));
