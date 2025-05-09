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
        .then(problems => {
            console.log('Filtered problems:', problems);
            const problemsList = document.getElementById('problems-list');
            problemsList.innerHTML = '';

            if (problems.length > 0) {
                problems.forEach(problem => {
                    const li = document.createElement('li');
                    li.style.position = 'relative';
                    const problemId = problem[0];
                    const attempts = problem[5]; // attempts
                    const solved = problem[6];   // solved
                    let dotHtml = '';
                    if (attempts > 0) {
                        if (solved) {
                            dotHtml = '<span style="width: 10px; height: 10px; background-color: green; border-radius: 50%; margin-right: 5px;" title="Problem Solved"></span>';
                        } else {
                            dotHtml = '<span style="width: 10px; height: 10px; background-color: yellow; border-radius: 50%; margin-right: 5px;" title="Attempted but Not Solved"></span>';
                        }
                    }
                    li.innerHTML = `
                        <a href="/problem/${problemId}" style="text-decoration: none; color: inherit;">
                            <p>ID: ${problemId}</p>
                            <h3>${problem[1]}</h3>
                            <p><b>Statement:</b> ${problem[2]}</p>
                            <p><strong>Points:</strong> ${problem[3]}</p>
                            ${problem[4] ? `<p><strong>Topic:</strong> ${problem[4]}</p>` : ''}
                        </a>
                        <div style="position: absolute; top: 10px; right: 10px; display: flex; align-items: center;">
                            ${dotHtml}
                            <a href="/admin/login?redirect=/problem/${problemId}/edit" style="color: #ffffff; font-size: 18px; z-index: 10;" title="Edit problem">
                                <i class="fas fa-edit"></i>
                            </a>
                        </div>
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

function addproblem() {
    window.location.href = '/newproblem';
}