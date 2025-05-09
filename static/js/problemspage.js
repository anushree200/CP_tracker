function filterProblems() {
    const points = document.getElementById('filter').value;
    const topic = document.getElementById('filtertopic').value;
    const keywords = document.getElementById('keyword').value.toLowerCase().trim();

    console.log('Filter values:', { points, topic, keywords });

    const params = new URLSearchParams();
    if (points) params.append('points', points);
    if (topic) params.append('topic', topic);
    if (keywords) params.append('keywords', keywords);

    console.log('Fetch URL:', `/filter?${params.toString()}`);

    fetch(`/filter?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            console.log('Filtered problems:', data);
            const problemsList = document.getElementById('problems-list');
            problemsList.innerHTML = '';

            if (data.length > 0) {
                data.forEach(problem => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <a href="/problem/${problem.id}" style="text-decoration: none; color: inherit;">
                            <p>ID: ${problem.id}</p>
                            <h3>${problem.title}</h3>
                            <p><b>Statement:</b> ${problem.description}</p>
                            <p><strong>Points:</strong> ${problem.points}</p>
                            <p><strong>Topic:</strong> ${problem.topic}</p>
                        </a>
                    `;
                    problemsList.appendChild(li);
                });
            } else {
                problemsList.innerHTML = '<p>No problems found.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching filtered problems:', error);
            document.getElementById('problems-list').innerHTML = '<p>Error loading problems.</p>';
        });
}

function clearFilters() {
    document.getElementById('filter').value = '';
    document.getElementById('filtertopic').value = '';
    document.getElementById('keyword').value = '';
    filterProblems();
}