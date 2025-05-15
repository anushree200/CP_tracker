document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('submission-chart');
    if (!canvas) {
        console.error("Canvas element with ID 'submission-chart' not found.");
        return;
    }
    const ctx = canvas.getContext('2d');

    const totalSubmissions = parseInt(canvas.dataset.totalSubmissions) || 0;
    const successfulSubmissions = parseInt(canvas.dataset.successfulSubmissions) || 0;

    console.log("Total Submissions:", totalSubmissions);
    console.log("Successful Submissions:", successfulSubmissions);

    const failedSubmissions = totalSubmissions - successfulSubmissions;

    if (totalSubmissions === 0) {
        console.warn("No submissions to display in the chart.");
        return;
    }

    try {
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Successful', 'Failed'],
                datasets: [{
                    data: [successfulSubmissions, failedSubmissions],
                    backgroundColor: ['#28a745', '#dc3545'],
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
    const pointdist = document.getElementById('point-chart');
    if (pointdist){
        const pointcontext = pointdist.getContext('2d');
        const rawdist = pointdist.dataset.distribution;
        try{
            const dist = JSON.parse(rawdist);
            const labels = Object.keys(dist);
            const data = Object.values(dist);
            new Chart(pointcontext,{
                type:'bar',
             data: {
                    labels: labels,
                    datasets: [{
                        label: 'Number of Problems Solved',
                        data: data,
                        backgroundColor: '#007bff',
                        borderColor: '#0056b3',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Solved Problems by Point Value'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Problems'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Point Value'
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Failed to parse point distribution or render chart:", error);
        }
        
    }
});