import java.io.*;
import java.net.*;
import java.util.Base64;
import org.json.JSONObject;

public class AccessTokenRetriever {
    public static void main(String[] args) {
        String baseUrl = "https://sandbox.safaricom.co.ke";
        String accessTokenUrl = "/oauth/v1/generate?grant_type=client_credentials";
        String consumerKey = "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV";
        String consumerSecret = "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm";

        try {
            URL url = new URL(baseUrl + accessTokenUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");

            String encoded = Base64.getEncoder().encodeToString((consumerKey + ":" + consumerSecret).getBytes());
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
                System.out.println("Access Token: " + json.getString("access_token"));
            } else {
                System.out.println("Error: " + response.toString());
            }
        } catch (IOException e) {
            System.out.println("Exception: " + e.getMessage());
        }
    }
}
