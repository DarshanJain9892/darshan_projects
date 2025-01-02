import java.io.*;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class UIApiLoadTester {
    private static String apiUrl;
    private static int tps;
    private static int durationInSeconds;
    private static int threadCount;
    private static boolean enableScreen;
    private static List<String> phoneNumbers = new ArrayList<>();
    private static AtomicInteger totalRequests = new AtomicInteger(0);
    private static AtomicInteger successfulRequests = new AtomicInteger(0);
    private static AtomicInteger failedRequests = new AtomicInteger(0);
    private static long startTime;
    private static String logFileName;
    private static final String LOG_FOLDER = "loadsummary";

    public static void main(String[] args) {
        // Load configuration from properties file
        loadConfig();

        // Ensure the loadsummary folder exists
        verifyLogFolder();

        // Generate unique log file name with date and time
        createUniqueLogFileName();

        // Load phone numbers from CSV
        loadPhoneNumbers();

        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(enableScreen ? 3 : 2);

        startTime = System.currentTimeMillis();

        // Schedule requests at the specified TPS
        Runnable task = () -> {
            for (int i = 0; i < tps; i++) {
                executor.submit(() -> sendRequest());
            }
        };

        scheduler.scheduleAtFixedRate(task, 0, 1000, TimeUnit.MILLISECONDS);

        // Schedule periodic TPS calculation and logging
        scheduler.scheduleAtFixedRate(UIApiLoadTester::logCurrentTPS, 1, 1, TimeUnit.SECONDS);

        // If screen monitoring is enabled, schedule real-time console output
        if (enableScreen) {
            scheduler.scheduleAtFixedRate(UIApiLoadTester::showScreen, 1, 1, TimeUnit.SECONDS);
        }

        // Shutdown after the specified duration
        scheduler.schedule(() -> {
            scheduler.shutdown();
            executor.shutdown();

            try {
                executor.awaitTermination(10, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            logSummary();
        }, durationInSeconds, TimeUnit.SECONDS);

        System.out.println("Load testing started. Press Ctrl+C to stop.");
    }

    private static void loadConfig() {
        try (InputStream input = new FileInputStream("config.properties")) {
            Properties prop = new Properties();
            prop.load(input);
            apiUrl = prop.getProperty("api_url");
            tps = Integer.parseInt(prop.getProperty("tps"));
            durationInSeconds = Integer.parseInt(prop.getProperty("duration_in_seconds"));
            threadCount = Integer.parseInt(prop.getProperty("thread_count"));
            enableScreen = Boolean.parseBoolean(prop.getProperty("enable_screen", "false"));
        } catch (IOException ex) {
            ex.printStackTrace();
            System.exit(1);
        }
    }

    private static void verifyLogFolder() {
        File logFolder = new File(LOG_FOLDER);
        if (!logFolder.exists() || !logFolder.isDirectory()) {
            System.err.println("Error: The folder 'loadsummary' does not exist.");
            System.exit(1);
        }
    }

    private static void createUniqueLogFileName() {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        logFileName = LOG_FOLDER + File.separator + "current_tps_" + timestamp + ".log";
    }

    private static void loadPhoneNumbers() {
        try (BufferedReader br = new BufferedReader(new FileReader("phone_numbers.csv"))) {
            String line;
            while ((line = br.readLine()) != null) {
                phoneNumbers.add(line.trim());
            }
        } catch (IOException ex) {
            ex.printStackTrace();
            System.exit(1);
        }
    }

    private static void sendRequest() {
        try {
            String phoneNumber = phoneNumbers.isEmpty() ? "" : phoneNumbers.get(new Random().nextInt(phoneNumbers.size()));
            String finalUrl = apiUrl.replace("9892374482", phoneNumber);

            // Use URI to ensure valid URL construction
            URI uri = new URI(finalUrl);
            HttpURLConnection connection = (HttpURLConnection) uri.toURL().openConnection();
            connection.setRequestMethod("GET");

            int responseCode = connection.getResponseCode();
            totalRequests.incrementAndGet();
            if (responseCode == 200) {
                successfulRequests.incrementAndGet();
            } else {
                failedRequests.incrementAndGet();
            }
        } catch (URISyntaxException | IOException ex) {
            failedRequests.incrementAndGet();
            ex.printStackTrace();
        }
    }

    private static void logCurrentTPS() {
        long currentTime = System.currentTimeMillis();
        double elapsedSeconds = (currentTime - startTime) / 1000.0;
        double currentTPS = totalRequests.get() / elapsedSeconds;

        try (FileWriter writer = new FileWriter(logFileName, true)) {
            writer.write(String.format("Elapsed Time: %.2f seconds, Achieved TPS: %.2f%n", elapsedSeconds, currentTPS));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void showScreen() {
        long currentTime = System.currentTimeMillis();
        double elapsedSeconds = (currentTime - startTime) / 1000.0;
        double currentTPS = totalRequests.get() / elapsedSeconds;

        System.out.println("\n--- Real-Time Metrics ---");
        System.out.printf("Elapsed Time: %.2f seconds%n", elapsedSeconds);
        System.out.printf("Achieved TPS: %.2f%n", currentTPS);
        System.out.println("Total Requests Sent: " + totalRequests.get());
        System.out.println("Successful Requests: " + successfulRequests.get());
        System.out.println("Failed Requests: " + failedRequests.get());
        System.out.println("-------------------------");
    }

    private static void logSummary() {
        System.out.println("\n--- Load Test Summary ---");
        System.out.println("Total Requests Sent: " + totalRequests.get());
        System.out.println("Successful Requests: " + successfulRequests.get());
        System.out.println("Failed Requests: " + failedRequests.get());
        System.out.println("-------------------------");

        try (FileWriter writer = new FileWriter(logFileName, true)) {
            writer.write("\n--- Load Test Summary ---\n");
            writer.write("Total Requests Sent: " + totalRequests.get() + "\n");
            writer.write("Successful Requests: " + successfulRequests.get() + "\n");
            writer.write("Failed Requests: " + failedRequests.get() + "\n");
            writer.write("-------------------------\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
