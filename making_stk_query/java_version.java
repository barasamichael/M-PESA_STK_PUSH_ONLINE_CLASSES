import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Base64;
import java.util.Date;
import org.json.JSONObject;

public class MPesaSTKQuery {
    // Configuration
    private static final String BASE_URL = "https://sandbox.safaricom.co.ke";
    private static final String ACCESS_TOKEN_URL = "/oauth/v1/generate?grant_type=client_credentials";
    private static final String STK_PUSH_URL = "/mpesa/stkpush/v1/processrequest";
    private static final String STK_QUERY_URL = "/mpesa/stkpushquery/v1/query";
    private static final String BUSINESS_SHORT_CODE = "174379";
    private static final String PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919";
    private static final String TILL_NUMBER = "174379";
    private static final String CALLBACK_URL = "https://mydomain.com/path";
    private static final String CONSUMER_KEY = "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV";
    private static final String CONSUMER_SECRET = "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm";
    
    public static void main(String[] args) {
        try {
            if (args.length > 0) {
                // Query STK status using command line argument as CheckoutRequestID
                String checkoutRequestId = args[0];
                JSONObject result = querySTKStatus(checkoutRequestId);
                System.out.println(result.toString(2));
            } else {
                System.out.println("Please provide a CheckoutRequestID as an argument");
            }
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
    
    public static String getAccessToken() throws IOException {
        URL url = new URL(BASE_URL + ACCESS_TOKEN_URL);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        
        String encoded = Base64.getEncoder().encodeToString((CONSUMER_KEY + ":" + CONSUMER_SECRET).getBytes());
        conn.setRequestProperty("Authorization", "Basic " + encoded);
        conn.setRequestProperty("Content-Type", "application/json");
        
        int status = conn.getResponseCode();
        InputStream stream = (status < HttpURLConnection.HTTP_BAD_REQUEST) ? conn.getInputStream() : conn.getErrorStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(stream));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        
        JSONObject json = new JSONObject(response.toString());
        if (json.has("access_token")) {
            return json.getString("access_token");
        } else {
            throw new IOException("Failed to get access token: " + json.toString());
        }
    }
    
    public static JSONObject querySTKStatus(String checkoutRequestId) throws IOException {
        if (checkoutRequestId == null || checkoutRequestId.isEmpty()) {
            throw new IllegalArgumentException("CheckoutRequestID is required");
        }
        
        // Get access token
        String accessToken = getAccessToken();
        
        // Generate timestamp
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMddHHmmss");
        String timestamp = dateFormat.format(new Date());
        
        // Generate password
        String passwordString = BUSINESS_SHORT_CODE + PASSKEY + timestamp;
        String password = Base64.getEncoder().encodeToString(passwordString.getBytes(StandardCharsets.UTF_8));
        
        // Create STK Query request
        URL url = new URL(BASE_URL + STK_QUERY_URL);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("Authorization", "Bearer " + accessToken);
        conn.setDoOutput(true);
        
        JSONObject queryPayload = new JSONObject();
        queryPayload.put("BusinessShortCode", BUSINESS_SHORT_CODE);
        queryPayload.put("Password", password);
        queryPayload.put("Timestamp", timestamp);
        queryPayload.put("CheckoutRequestID", checkoutRequestId);
        
        // Send request
        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = queryPayload.toString().getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        }
        
        // Get response
        int status = conn.getResponseCode();
        InputStream stream = (status < HttpURLConnection.HTTP_BAD_REQUEST) ? conn.getInputStream() : conn.getErrorStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(stream));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        
        return new JSONObject(response.toString());
    }
}
