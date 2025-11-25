function searchTopic(topic) {
    document.getElementById('queryInput').value = topic;
    fetchRecommendations();
}


function fetchRecommendations() {
    const query = document.getElementById('queryInput').value.trim();
    const listElement = document.getElementById('recommendationsList');
    const resultsCount = document.getElementById('resultsCount');
    
    if (!query) {
        listElement.innerHTML = `
            <div class="results-header">
                <h2>📌 Top Stories For You</h2>
            </div>
            <p class="error">⚠️ Please enter your news interests before searching.</p>
        `;
        return;
    }

    // Display loading state
    listElement.innerHTML = `
        <div class="results-header">
            <h2>📌 Top Stories For You</h2>
        </div>
        <p style="text-align: center; color: #667eea; font-weight: 600;">
            🔍 Analyzing "${query}" using BERT semantic search...
        </p>
        <div class="loading-spinner"></div>
    `;

    // Send POST request
    fetch('/api/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { 
                throw new Error(err.error || `HTTP error! status: ${response.status}`); 
            });
        }
        return response.json();
    })
    .then(data => {
        // Handle and display the data
        listElement.innerHTML = `
            <div class="results-header">
                <h2>📌 Top Stories For You</h2>
                <div class="results-count" id="resultsCount"></div>
            </div>
        `;
        
        const newResultsCount = document.getElementById('resultsCount');

        if (data.error) {
            listElement.innerHTML += `<p class="error">❌ Server Error: ${data.error}</p>`;
            return;
        }

        if (data.length === 0) {
            listElement.innerHTML += `
                <p class="results-placeholder">
                    No matching articles found for "<strong>${query}</strong>". 
                    <br>Try a different search query or browse popular topics above!
                </p>
            `;
        } else {
            newResultsCount.textContent = `${data.length} ${data.length === 1 ? 'Article' : 'Articles'} Found`;
            
            const ul = document.createElement('ul');
            data.forEach((article, index) => {
                const title = article.title || 'Untitled Article';
                const link = article.link || '#';
                const summary = article.summary;
                const content = article.content;
                const category = article.category || 'General';
                const score = (article.similarity_score * 100).toFixed(1);
                
                const description = summary ? summary : (content ? content.substring(0, 180) + '...' : 'No description available.');
                const imageUrl = article.image_url || 'https://via.placeholder.com/400x250?text=No+Image';

                const li = document.createElement('li');
                li.style.animationDelay = `${index * 0.1}s`;
                
                li.innerHTML = `
                    <div class="flex">
                        <img src="${imageUrl}" 
                             alt="Article image" 
                             class="article-image" 
                             onerror="this.onerror=null;this.src='https://via.placeholder.com/400x250?text=No+Image';" />
                        <div class="article-details">
                            <div class="news-header">
                                <strong><a href="${link}" target="_blank">${title}</a></strong> 
                                <span class="score">${score}% Match</span>
                            </div>
                            <span class="category-tag">📂 ${category}</span>
                            <p class="content-snippet">${description}</p>
                            <a href="${link}" target="_blank" class="read-more">
                                Read Full Article →
                            </a>
                        </div>
                    </div>
                `;
                ul.appendChild(li);
            });
            listElement.appendChild(ul);
        }
    })
    .catch(error => {
        console.error('Error fetching recommendations:', error);
        listElement.innerHTML = `
            <div class="results-header">
                <h2>📌 Top Stories For You</h2>
            </div>
            <p class="error">
                ❌ A network error occurred or the server is unavailable. 
                <br>Please check the Flask console for details. 
                <br><small>(${error.message})</small>
            </p>
        `;
    });
}

// Allow Enter key to trigger search
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('queryInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchRecommendations();
        }
    });
});