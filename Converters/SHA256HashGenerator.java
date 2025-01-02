import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class SHA256HashGenerator {
    public static void main(String[] args) {
        // Input string
        String input = "1401590930000015067,120210000037";

        // Generate the SHA-256 hash
        String hash = getHash(input);

        // Print the results
        if (hash != null) {
            System.out.println("Input String: " + input);
            System.out.println("SHA-256 Hash (Hex): " + hash);
        }
    }

    public static String getHash(String input) {
        String hash = "";
        try {
            // Create a SHA-256 digest instance
            MessageDigest digest = MessageDigest.getInstance("SHA-256");

            // Generate the hash bytes
            byte[] hashBytes = digest.digest(input.getBytes());

            // Convert hash bytes to hexadecimal format
            StringBuilder hexString = new StringBuilder(2 * hashBytes.length);
            for (byte b : hashBytes) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0'); // Ensure two digits for each byte
                }
                hexString.append(hex);
            }
            hash = hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            System.err.println("Error: SHA-256 algorithm not found.");
        } catch (Exception e) {
            System.err.println("Error generating SHA-256 hash for input: " + input);
        }
        return hash;
    }
}
