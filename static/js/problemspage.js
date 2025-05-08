function filterProblems(){
    const points = document.getElementById('filter').value;
    const keywords = document.getElementById('keyword').value.toLowerCase().trim();
    const params = new URLSearchParams();
    if (points) params.append('points', points);
    if (keywords) params.append('keywords', keywords);
    fetch(`/filter?${params.toString()}`)
    .then(response => response.json())
    .then(data => {
        // Update the problems list
        const problemsList = document.getElementById('problems-list');
        problemsList.innerHTML = ''; // Clear the current list

        if (data.length > 0) {
            data.forEach(problem => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <h3>${problem.title}</h3>
                    <p>${problem.description}</p>
                    <p><strong>Points:</strong> ${problem.points}</p>
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