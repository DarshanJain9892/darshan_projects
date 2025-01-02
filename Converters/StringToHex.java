import java.nio.charset.StandardCharsets;

public class StringToHex {
    public static void main(String[] args) {
        // Input string
        String input = "darshan8596225";
        
        // Convert string to hex
        String hexOutput = convertStringToHex(input);
        
        // Print results
        System.out.println("Original String: " + input);
        System.out.println("Hexadecimal Representation: " + hexOutput);
    }

    public static String convertStringToHex(String input) {
        // Use StringBuilder for efficient string manipulation
        StringBuilder hexBuilder = new StringBuilder();

        // Convert each character to hexadecimal
        for (char c : input.toCharArray()) {
            String hex = Integer.toHexString((int) c);
            // Ensure two-character representation for each byte
            if (hex.length() == 1) {
                hexBuilder.append('0');
            }
            hexBuilder.append(hex);
        }
        return hexBuilder.toString();
    }
}
