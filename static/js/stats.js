document.addEventListener('DOMContentLoaded', function () {
    // Get the canvas element for the submission chart
    const canvas = document.getElementById('submission-chart');
    if (!canvas) {
        console.error("Canvas element with ID 'submission-chart' not found.");
        return;
    }
    const ctx = canvas.getContext('2d');

    // Extract stats data from data attributes
    const totalSubmissions = parseInt(canvas.dataset.totalSubmissions) || 0;
    const successfulSubmissions = parseInt(canvas.dataset.successfulSubmissions) || 0;

    // Log the values to debug
    console.log("Total Submissions:", totalSubmissions);
    console.log("Successful Submissions:", successfulSubmissions);

    // Calculate data for the chart
    const failedSubmissions = totalSubmissions - successfulSubmissions;

    // Ensure we have data to display
    if (totalSubmissions === 0) {
        console.warn("No submissions to display in the chart.");
        return;
    }

    // Create a pie chart to show submission accuracy
    try {
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Successful', 'Failed'],
                datasets: [{
                    data: [successfulSubmissions, failedSubmissions],
                    backgroundColor: ['#28a745', '#dc3545'], // Green for success, red for failure
                    borderColor: '#fff',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Submission Accuracy'
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error rendering chart:", error);
    }
});