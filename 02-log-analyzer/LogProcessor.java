import java.io.*;
import java.nio.file.*;

public class LogProcessor {
    public static void main(String[] args) throws Exception {
        // Folders to watch and move to
        Path rawDir = Paths.get("logs/raw");
        Path processedDir = Paths.get("logs/processed");

        System.out.println("Java Log Processor started. Watching: " + rawDir);

        WatchService watchService = FileSystems.getDefault().newWatchService();
        rawDir.register(watchService, StandardWatchEventKinds.ENTRY_CREATE);

        while (true) {
            WatchKey key = watchService.take();
            for (WatchEvent<?> event : key.pollEvents()) {
                Path fileName = (Path) event.context();
                File rawFile = rawDir.resolve(fileName).toFile();

                System.out.println("Processing new log file: " + fileName);
                
                // Simple Sanitization Logic: Remove empty lines or specific "DEBUG" info
                processLogFile(rawFile, processedDir.resolve(fileName).toFile());
                
                // Optional: Delete the raw file after processing
                rawFile.delete();
            }
            key.reset();
        }
    }

    private static void processLogFile(File input, File output) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(input));
             BufferedWriter writer = new BufferedWriter(new FileWriter(output))) {
            
            String line;
            while ((line = reader.readLine()) != null) {
                // Example: Only move lines that aren't "INFO" (keep only WARN/ERROR)
                if (line.contains("Failed") || line.contains("ERROR") || line.contains("Critical")) {
                    writer.write(line + System.lineSeparator());
                }
            }
        }
    }
}