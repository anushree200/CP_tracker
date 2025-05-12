let codeEditor;
window.onload = function () {
        if (typeof CodeMirror === 'undefined') {
            console.error('CodeMirror failed to load. Please check the CDN links.');
            document.getElementById('results').innerHTML = '<p style="color: red;">Error: Code editor failed to load. Please refresh the page or check your internet connection.</p>';
            return;
        }

        codeEditor = CodeMirror.fromTextArea(document.getElementById('code'), {
            mode: 'python',
            lineNumbers: true,
            theme: 'default',
            indentUnit: 4,
            tabSize: 4,
            indentWithTabs: false
        });

        if (typeof submitCode === 'undefined') {
            console.error('submitCode function not found. Ensure problemdetail.js is loaded correctly.');
            document.getElementById('results').innerHTML = '<p style="color: red;">Error: Submit functionality failed to load. Please refresh the page.</p>';
        }
    }
function submitCode(problemId) {
    const code = codeEditor.getValue();
    const language = document.getElementById('language').value;

    const formData = new FormData();
    formData.append('code', code);
    formData.append('language', language);

    fetch(`/submit/${problemId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';

        if (data.error) {
            resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            return;
        }

        const allAccepted = data.results.every(result => result.verdict === "Accepted");
        resultsDiv.innerHTML = `<h3>Verdict Summary: <span class="${allAccepted ? 'accepted' : 'wrong-answer'}">${allAccepted ? 'All Test Cases Passed' : 'Failed'}</span></h3>`;

        data.results.forEach((result, index) => {
            const resultDiv = document.createElement('div');
            resultDiv.className = 'result';
            resultDiv.innerHTML = `
                <h4>Test Case ${index + 1}</h4>
                <p><strong>Input:</strong> ${result.input}</p>
                <p><strong>Expected Output:</strong> ${result.expected_output}</p>
                <p><strong>Actual Output:</strong> ${result.actual_output}</p>
                ${result.error ? `<p><strong>Error:</strong> ${result.error}</p>` : ''}
                <p><strong>Verdict:</strong> <span class="${result.verdict.toLowerCase().replace(' ', '-')}">${result.verdict}</span></p>
                <hr>
            `;
            resultsDiv.appendChild(resultDiv);
        });
    })
    .catch(error => {
        console.error('Error submitting code:', error);
        document.getElementById('results').innerHTML = '<p style="color: red;">Error submitting code.</p>';
    });
}

if (typeof CodeMirror === 'undefined') {
            console.error('CodeMirror failed to load. Please check the CDN links.');
            document.getElementById('results').innerHTML = '<p style="color: red;">Error: Code editor failed to load. Please refresh the page or check your internet connection.</p>';
        }
        if (typeof submitCode === 'undefined') {
            console.error('submitCode function not found. Ensure problemdetail.js is loaded correctly.');
            document.getElementById('results').innerHTML = '<p style="color: red;">Error: Submit functionality failed to load. Please refresh the page.</p>';
        }