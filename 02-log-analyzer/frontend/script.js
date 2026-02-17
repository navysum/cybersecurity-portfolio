// Initialize the Chart
const ctx = document.getElementById('threatChart').getContext('2d');
let threatChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['12:00', '12:10', '12:20', '12:30', '12:40'], // Placeholder time
        datasets: [{
            label: 'Detected Threats',
            data: [2, 5, 1, 8, 4], // Placeholder data
            borderColor: '#38bdf8',
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { labels: { color: 'white' } }
        }
    }
});

// Function to fetch data from your Python Flask API
async function updateDashboard() {
    try {
        const response = await fetch('/api/logs'); // This hits your @app.route('/api/logs')
        const data = await response.json();

        // Update the HTML numbers
        document.getElementById('total-events').innerText = data.total_count;
        document.getElementById('alert-count').innerText = data.failed_attempts;

        // Update Chart (Optional: push new data points here)
    } catch (error) {
        console.error("Error fetching logs:", error);
    }
}

// Refresh data every 5 seconds
setInterval(updateDashboard, 5000);