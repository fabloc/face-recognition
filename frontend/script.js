const API_URL = 'http://localhost:8000';

async function performMatching() {
    const resultsList = document.getElementById('results-list');
    resultsList.innerHTML = '<div style="text-align: center; padding: 20px;">Loading...</div>';

    const activeTab = document.querySelector('.tab.active').textContent;
    const formData = new FormData();

    if (activeTab === 'Local Upload') {
        const fileInput = document.getElementById('local-file');
        if (fileInput.files.length === 0) {
            alert('Please select a file.');
            resultsList.innerHTML = '<div style="color: #70757a; text-align: center; padding: 20px;">No results yet. Perform matching to see results.</div>';
            return;
        }
        formData.append('file', fileInput.files[0]);
    } else {
        const bucketName = document.getElementById('bucket-name').value;
        const objectName = document.getElementById('object-name').value;
        if (!bucketName || !objectName) {
            alert('Please fill in both bucket name and object name.');
            resultsList.innerHTML = '<div style="color: #70757a; text-align: center; padding: 20px;">No results yet. Perform matching to see results.</div>';
            return;
        }
        formData.append('bucket_name', bucketName);
        formData.append('object_name', objectName);
    }

    try {
        const response = await fetch(`${API_URL}/match`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Matching failed');
        }

        const results = await response.json();
        renderResults(results);
    } catch (error) {
        alert(`Error: ${error.message}`);
        resultsList.innerHTML = `<div style="color: #d93025; text-align: center; padding: 20px;">Error: ${error.message}</div>`;
    }
}

function renderResults(results) {
    const resultsList = document.getElementById('results-list');
    resultsList.innerHTML = '';

    if (results.length === 0) {
        resultsList.innerHTML = '<div style="color: #70757a; text-align: center; padding: 20px;">No matching faces found.</div>';
        return;
    }

    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'result-item';
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'name';
        nameSpan.textContent = result.name;
        
        const percentageSpan = document.createElement('span');
        percentageSpan.className = 'percentage';
        percentageSpan.textContent = `${result.similarity.toFixed(2)}%`;
        
        const uriSpan = document.createElement('span');
        uriSpan.className = 'uri';
        uriSpan.textContent = result.image_uri;
        uriSpan.title = result.image_uri; // Show full URI on hover
        
        item.appendChild(nameSpan);
        item.appendChild(percentageSpan);
        item.appendChild(uriSpan);
        
        resultsList.appendChild(item);
    });
}

async function performBulkInsert() {
    const statusDiv = document.getElementById('bulk-status');
    const bucketName = document.getElementById('bulk-bucket').value;
    const prefix = document.getElementById('bulk-prefix').value;

    if (!bucketName) {
        alert('Please enter a bucket name.');
        return;
    }

    statusDiv.textContent = 'Processing bulk insert...';
    statusDiv.style.color = '#5f6368';

    const formData = new FormData();
    formData.append('bucket_name', bucketName);
    formData.append('prefix', prefix);

    try {
        const response = await fetch(`${API_URL}/bulk-insert`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Bulk insert failed');
        }

        const result = await response.json();
        statusDiv.textContent = result.message;
        statusDiv.style.color = '#188038';
    } catch (error) {
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.style.color = '#d93025';
    }
}
