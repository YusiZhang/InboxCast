// InboxCast Demo JavaScript

// Global state
let currentEmails = [];
let currentRSSItems = [];
let generatedContent = '';
let audioFilePath = '';

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
});

// Utility functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.classList.add('loading');
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    element.classList.remove('loading');
}

function showResults(containerId) {
    const container = document.getElementById(containerId);
    container.classList.add('show');
}

function hideResults(containerId) {
    const container = document.getElementById(containerId);
    container.classList.remove('show');
}

function showError(message, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = `<div class="error-message">${message}</div>`;
    container.classList.add('show');
}

function showSuccess(message, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = `<div class="success-message">${message}</div>`;
    container.classList.add('show');
}

// Authentication functions
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        
        const authText = document.getElementById('auth-text');
        const authStatus = document.getElementById('auth-status');
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (data.authenticated) {
            authText.textContent = 'Authenticated with Gmail';
            authStatus.className = 'status-indicator status-authenticated';
            loginBtn.style.display = 'none';
            logoutBtn.style.display = 'inline-block';
        } else {
            authText.textContent = 'Not authenticated';
            authStatus.className = 'status-indicator status-not-authenticated';
            loginBtn.style.display = 'inline-block';
            logoutBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        const authText = document.getElementById('auth-text');
        const authStatus = document.getElementById('auth-status');
        authText.textContent = 'Authentication check failed';
        authStatus.className = 'status-indicator status-not-authenticated';
    }
}

async function loginWithGmail() {
    try {
        showLoading('login-btn');
        
        const response = await fetch('/api/auth/login');
        const data = await response.json();
        
        if (data.authenticated) {
            await checkAuthStatus();
            showSuccess('Successfully authenticated with Gmail!', 'auth-section');
        } else {
            showError('Authentication failed. Please check your credentials.json file.', 'auth-section');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Login failed: ' + error.message, 'auth-section');
    } finally {
        hideLoading('login-btn');
    }
}

async function logout() {
    try {
        const response = await fetch('/api/auth/logout', { method: 'POST' });
        const data = await response.json();
        
        await checkAuthStatus();
        showSuccess('Logged out successfully', 'auth-section');
    } catch (error) {
        console.error('Logout error:', error);
        showError('Logout failed: ' + error.message, 'auth-section');
    }
}

// RSS functions
async function fetchRSSFeed() {
    const urlInput = document.getElementById('rss-url');
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter an RSS feed URL', 'rss-results');
        return;
    }
    
    try {
        showLoading('fetch-rss-btn');
        hideResults('rss-results');
        
        const response = await fetch('/api/rss/fetch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                max_entries: 5
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        
        const data = await response.json();
        currentRSSItems = data.entries;
        displayRSSResults(data);
        
    } catch (error) {
        console.error('RSS fetch error:', error);
        showError('Failed to fetch RSS feed: ' + error.message, 'rss-results');
    } finally {
        hideLoading('fetch-rss-btn');
    }
}

async function testRSSFeed() {
    try {
        showLoading('test-rss-btn');
        hideResults('rss-results');
        
        const response = await fetch('/api/rss/test');
        const data = await response.json();
        
        currentRSSItems = data.entries;
        displayRSSResults(data);
        
    } catch (error) {
        console.error('RSS test error:', error);
        showError('RSS test failed: ' + error.message, 'rss-results');
    } finally {
        hideLoading('test-rss-btn');
    }
}

function displayRSSResults(data) {
    const container = document.getElementById('rss-results');
    
    let html = `
        <h4>📰 RSS Feed: ${data.title}</h4>
        <p><strong>Description:</strong> ${data.description || 'No description available'}</p>
        <p><strong>Total Entries:</strong> ${data.total_entries}</p>
        <div style="margin-top: 1rem;">
            <h5>Latest Articles:</h5>
    `;
    
    data.entries.forEach((entry, index) => {
        html += `
            <div class="result-item">
                <h4>${entry.title || 'Untitled'}</h4>
                <p>${entry.description || entry.content || 'No description available'}</p>
                <div class="meta">
                    Source: ${entry.source || 'RSS'} | 
                    Published: ${entry.published || 'Unknown'}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    showResults('rss-results');
}

// Content generation functions
async function generateContent() {
    const contentItems = [...currentRSSItems, ...currentEmails];
    
    if (contentItems.length === 0) {
        showError('Please fetch RSS feed or authenticate with Gmail first to get content', 'content-results');
        return;
    }
    
    const tone = document.getElementById('tone-select').value;
    const language = document.getElementById('language-select').value;
    const maxWords = parseInt(document.getElementById('max-words').value);
    const style = document.getElementById('style-select').value;
    
    try {
        showLoading('generate-content-btn');
        hideResults('content-results');
        
        const response = await fetch('/api/content/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content_items: contentItems,
                tone: tone,
                language: language,
                max_words: maxWords,
                style: style
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        
        const data = await response.json();
        generatedContent = data.generated_content;
        displayContentResults(data);
        
    } catch (error) {
        console.error('Content generation error:', error);
        showError('Failed to generate content: ' + error.message, 'content-results');
    } finally {
        hideLoading('generate-content-btn');
    }
}

async function testContentGeneration() {
    try {
        showLoading('test-content-btn');
        hideResults('content-results');
        
        const response = await fetch('/api/content/test', { method: 'POST' });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        
        const data = await response.json();
        generatedContent = data.generated_content;
        displayContentResults(data);
        
    } catch (error) {
        console.error('Content test error:', error);
        showError('Content generation test failed: ' + error.message, 'content-results');
    } finally {
        hideLoading('test-content-btn');
    }
}

function displayContentResults(data) {
    const container = document.getElementById('content-results');
    
    const html = `
        <h4>🤖 AI-Generated Content</h4>
        <div class="content-text">${data.generated_content}</div>
        <div class="meta">
            Word Count: ${data.word_count} | Sources: ${data.source_count}
        </div>
    `;
    
    container.innerHTML = html;
    showResults('content-results');
}

// Audio generation functions
async function generateAudio() {
    if (!generatedContent) {
        showError('Please generate content first before creating audio', 'audio-results');
        return;
    }
    
    const tone = document.getElementById('audio-tone-select').value;
    const speed = parseFloat(document.getElementById('speed-select').value);
    const language = document.getElementById('language-select').value;
    
    try {
        showLoading('generate-audio-btn');
        hideResults('audio-results');
        
        const response = await fetch('/api/audio/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: generatedContent,
                tone: tone,
                speed: speed,
                language: language
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        
        const data = await response.json();
        
        if (data.success) {
            audioFilePath = data.audio_file_path;
            displayAudioResults(data);
            setupAudioPlayer(data.audio_file_path);
        } else {
            throw new Error(data.error_message || 'Audio generation failed');
        }
        
    } catch (error) {
        console.error('Audio generation error:', error);
        showError('Failed to generate audio: ' + error.message, 'audio-results');
    } finally {
        hideLoading('generate-audio-btn');
    }
}

async function testAudioGeneration() {
    try {
        showLoading('test-audio-btn');
        hideResults('audio-results');
        
        const response = await fetch('/api/audio/test', { method: 'POST' });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        
        const data = await response.json();
        
        if (data.success) {
            audioFilePath = data.audio_file_path;
            displayAudioResults(data);
            setupAudioPlayer(data.audio_file_path);
        } else {
            throw new Error(data.error_message || 'Audio generation test failed');
        }
        
    } catch (error) {
        console.error('Audio test error:', error);
        showError('Audio generation test failed: ' + error.message, 'audio-results');
    } finally {
        hideLoading('test-audio-btn');
    }
}

function displayAudioResults(data) {
    const container = document.getElementById('audio-results');
    
    const html = `
        <h4>🎵 Audio Generated Successfully</h4>
        <div class="meta">
            Duration: ${data.duration ? data.duration.toFixed(1) + 's' : 'Unknown'} | 
            Format: ${data.format || 'MP3'}
        </div>
        <p style="margin-top: 1rem; color: #48bb78;">
            ✅ Audio file created and ready for playback below
        </p>
    `;
    
    container.innerHTML = html;
    showResults('audio-results');
}

function setupAudioPlayer(filePath) {
    const playerContainer = document.getElementById('audio-player-container');
    const noAudioMessage = document.getElementById('no-audio-message');
    const audioPlayer = document.getElementById('audio-player');
    const audioInfo = document.getElementById('audio-info-text');
    
    // Set up audio source
    audioPlayer.src = `/api/audio/download${filePath}`;
    
    // Show player, hide message
    playerContainer.style.display = 'block';
    noAudioMessage.style.display = 'none';
    
    // Update info
    audioInfo.textContent = 'Audio ready for playback - click play button above';
}

// Complete demo function
async function runCompleteDemo() {
    const progressContainer = document.getElementById('complete-demo-progress');
    progressContainer.innerHTML = '';
    progressContainer.classList.add('show');
    
    const steps = [
        { id: 'auth', name: 'Authentication Check', action: checkAuthStatus },
        { id: 'rss', name: 'Fetch Test RSS Feed', action: testRSSFeed },
        { id: 'content', name: 'Generate AI Content', action: testContentGeneration },
        { id: 'audio', name: 'Generate Audio', action: testAudioGeneration }
    ];
    
    // Create progress steps
    steps.forEach(step => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'progress-step';
        stepDiv.id = `progress-${step.id}`;
        stepDiv.innerHTML = `<strong>${step.name}</strong> - Waiting...`;
        progressContainer.appendChild(stepDiv);
    });
    
    try {
        showLoading('complete-demo-btn');
        
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            const stepElement = document.getElementById(`progress-${step.id}`);
            
            // Mark as active
            stepElement.className = 'progress-step active';
            stepElement.innerHTML = `<div class="spinner"></div><strong>${step.name}</strong> - In progress...`;
            
            try {
                await step.action();
                
                // Mark as completed
                stepElement.className = 'progress-step completed';
                stepElement.innerHTML = `<strong>${step.name}</strong> - ✅ Completed`;
                
                // Add delay between steps for better UX
                if (i < steps.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
                
            } catch (error) {
                // Mark as error
                stepElement.className = 'progress-step error';
                stepElement.innerHTML = `<strong>${step.name}</strong> - ❌ Failed: ${error.message}`;
                throw error;
            }
        }
        
        // Add success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `
            <h4>🎉 Complete Demo Finished Successfully!</h4>
            <p>The end-to-end workflow has been demonstrated. You can now play the generated audio above.</p>
        `;
        progressContainer.appendChild(successDiv);
        
    } catch (error) {
        console.error('Complete demo error:', error);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <h4>❌ Demo Failed</h4>
            <p>${error.message}</p>
        `;
        progressContainer.appendChild(errorDiv);
    } finally {
        hideLoading('complete-demo-btn');
    }
}