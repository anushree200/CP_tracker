function submitProblem(event) {
    event.preventDefault(); // Prevent default form submission

    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const points = document.getElementById('points').value;
    const topic = document.getElementById('topic').value;
    const platform = document.getElementById('platform').value;
    const platformLink = document.getElementById('platform-link').value;

    // Collect test cases
    const testInputs = [];
    const testOutputs = [];
    for (let i = 1; i <= 3; i++) {
        const input = document.getElementById(`test-input-${i}`).value;
        const output = document.getElementById(`test-output-${i}`).value;
        testInputs.push(input);
        testOutputs.push(output);
    }

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