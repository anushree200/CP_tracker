function submitProblem(event) {
    event.preventDefault(); // Prevent default form submission

    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const points = document.getElementById('points').value;
    const topic = document.getElementById('topic').value;

    // Collect test cases
    const testInputs = [
        document.getElementById('test-input-1').value,
        document.getElementById('test-input-2').value,
        document.getElementById('test-input-3').value
    ];
    const testOutputs = [
        document.getElementById('test-output-1').value,
        document.getElementById('test-output-2').value,
        document.getElementById('test-output-3').value
    ];

    // Validate that all fields are filled
    if (!title || !description || !points || !topic || testInputs.some(input => !input) || testOutputs.some(output => !output)) {
        alert('Please fill in all fields, including all test cases.');
        return;
    }

    // Prepare the data to send
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('points', points);
    formData.append('topic', topic);
    formData.append('test_inputs', JSON.stringify(testInputs));
    formData.append('test_outputs', JSON.stringify(testOutputs));

    // Send the data to the server
    fetch('/addproblem', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Problem added successfully!');
            window.location.href = '/'; // Redirect to the problems page
        } else {
            alert('Error adding problem: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error submitting problem:', error);
        alert('Error submitting problem: ' + error.message);
    });
}