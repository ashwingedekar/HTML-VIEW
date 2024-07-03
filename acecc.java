import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnector {

    public static void main(String[] args) {
        // Database connection details
        String url = "jdbc:postgresql://localhost:13308/ProbeDB";
        String username = "dbuser";
        String password = "f767c8ff0a17766f0a095f3d8f9eff0e407281e1b12919d1052e9ad70bb7f367e1f3577eb3819d28396a01540cf260cee2749cf72777d0f7f853a3127f5f2b010964a99d"; // Update with the actual password
        
        // Establishing the database connection
        try {
            Connection connection = DriverManager.getConnection(url, username, password);
            if (connection != null) {
                System.out.println("Connected to the database!");
                // You can perform database operations here
            } else {
                System.out.println("Failed to make connection!");
            }
        } catch (SQLException e) {
            System.err.println("Connection Failed! Check output console");
            e.printStackTrace();
        }
    }
}
