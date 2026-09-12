/**
 * Biology Research Assistant - Frontend Application
 * Connects directly to FastAPI backend (/chat, /resume, /upload-pdf)
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Application State ---
    let backendUrl = localStorage.getItem('bioassistant_backend_url') || '';
    let currentSessionId = localStorage.getItem('bioassistant_current_session') || generateUUID();
    let sessions = JSON.parse(localStorage.getItem('bioassistant_sessions') || '[]');
    let uploadedFiles = JSON.parse(localStorage.getItem('bioassistant_uploaded_files') || '[]');

    // --- DOM Elements ---
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const chatMessages = document.getElementById('chat-messages');
    const welcomeHero = document.getElementById('welcome-hero');
    const btnNewChat = document.getElementById('btn-new-chat');
    const sessionList = document.getElementById('session-list');
    const pdfDropzone = document.getElementById('pdf-dropzone');
    const pdfFileInput = document.getElementById('pdf-file-input');
    const uploadedFilesList = document.getElementById('uploaded-files-list');
    const uploadProgress = document.getElementById('upload-progress');
    const btnQuickUpload = document.getElementById('btn-quick-upload');
    const btnUploadModalTrigger = document.getElementById('btn-upload-modal-trigger');
    const btnClearChat = document.getElementById('btn-clear-chat');
    const menuToggleBtn = document.getElementById('menu-toggle-btn');
    const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
    const sidebar = document.getElementById('sidebar');
    const activeSessionTitle = document.getElementById('active-session-title');
    const backendStatusDot = document.getElementById('backend-status-dot');
    const backendStatusText = document.getElementById('backend-status-text');

    // Settings Modal Elements
    const settingsModal = document.getElementById('settings-modal');
    const btnSettings = document.getElementById('btn-settings');
    const closeSettingsModal = document.getElementById('close-settings-modal');
    const backendUrlInput = document.getElementById('backend-url-input');
    const btnSaveSettings = document.getElementById('btn-save-settings');
    const btnTestConnection = document.getElementById('btn-test-connection');

    // --- Configure Marked JS Parser ---
    if (window.marked) {
        marked.setOptions({
            gfm: true,
            breaks: true,
            highlight: function (code, lang) {
                if (window.hljs && lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (e) {}
                }
                return code;
            }
        });
    }

    // --- Initialization ---
    init();

    function init() {
        checkBackendHealth();
        renderSessionList();
        renderUploadedFiles();
        setupEventListeners();
        backendUrlInput.value = backendUrl || 'http://localhost:8000';
    }

    // --- Utility Functions ---
    function generateUUID() {
        return 'session-' + Math.random().toString(36).substring(2, 9) + '-' + Date.now();
    }

    function getApiUrl(endpoint) {
        const base = backendUrl.trim().replace(/\/$/, '');
        return base ? `${base}${endpoint}` : endpoint;
    }

    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-check-circle text-emerald';
        if (type === 'error') icon = 'fa-exclamation-circle text-rose';

        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // --- Backend Health Check ---
    async function checkBackendHealth() {
        try {
            const res = await fetch(getApiUrl('/docs'), { method: 'HEAD' });
            if (res.ok || res.status === 404 || res.status === 405) {
                backendStatusDot.className = 'status-indicator online';
                backendStatusText.textContent = 'Connected';
            } else {
                throw new Error();
            }
        } catch (e) {
            backendStatusDot.className = 'status-indicator';
            backendStatusText.textContent = 'Offline';
        }
    }

    // --- Event Listeners Setup ---
    function setupEventListeners() {
        // Auto-expand textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        });

        // Keypress Send
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });

        btnSend.addEventListener('click', handleSendMessage);

        // Prompt Cards Click
        document.querySelectorAll('.prompt-card').forEach(card => {
            card.addEventListener('click', () => {
                const prompt = card.getAttribute('data-prompt');
                if (prompt) {
                    chatInput.value = prompt;
                    handleSendMessage();
                }
            });
        });

        // New Chat
        btnNewChat.addEventListener('click', startNewSession);
        btnClearChat.addEventListener('click', clearCurrentChat);

        // Sidebar Mobile Toggle
        if (menuToggleBtn) {
            menuToggleBtn.addEventListener('click', () => sidebar.classList.toggle('active'));
        }
        if (sidebarCloseBtn) {
            sidebarCloseBtn.addEventListener('click', () => sidebar.classList.remove('active'));
        }

        // Settings Modal
        btnSettings.addEventListener('click', () => settingsModal.classList.add('active'));
        closeSettingsModal.addEventListener('click', () => settingsModal.classList.remove('active'));
        btnSaveSettings.addEventListener('click', () => {
            backendUrl = backendUrlInput.value.trim();
            localStorage.setItem('bioassistant_backend_url', backendUrl);
            settingsModal.classList.remove('active');
            showToast('API URL saved.', 'success');
            checkBackendHealth();
        });

        btnTestConnection.addEventListener('click', async () => {
            backendUrl = backendUrlInput.value.trim();
            await checkBackendHealth();
            showToast('Connection check completed.', 'info');
        });

        // PDF Dropzone Events
        pdfDropzone.addEventListener('click', () => pdfFileInput.click());
        btnQuickUpload.addEventListener('click', () => pdfFileInput.click());
        btnUploadModalTrigger.addEventListener('click', () => pdfFileInput.click());

        pdfFileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                uploadPDF(e.target.files[0]);
            }
        });

        pdfDropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        pdfDropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length > 0) {
                uploadPDF(e.dataTransfer.files[0]);
            }
        });
    }

    // --- PDF Upload Handling (/upload-pdf) ---
    async function uploadPDF(file) {
        if (!file.name.endsWith('.pdf')) {
            showToast('Please select a PDF document.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        uploadProgress.style.width = '30%';

        try {
            showToast(`Uploading ${file.name}...`, 'info');
            
            const response = await fetch(getApiUrl('/upload-pdf'), {
                method: 'POST',
                body: formData
            });

            uploadProgress.style.width = '80%';

            if (!response.ok) {
                throw new Error(`Status ${response.status}`);
            }

            const data = await response.json();
            uploadProgress.style.width = '100%';

            setTimeout(() => { uploadProgress.style.width = '0%'; }, 800);

            showToast(`Document "${data.filename}" indexed.`, 'success');

            // Save file info locally
            uploadedFiles.unshift({ name: data.filename, date: new Date().toLocaleTimeString() });
            localStorage.setItem('bioassistant_uploaded_files', JSON.stringify(uploadedFiles));
            renderUploadedFiles();

        } catch (error) {
            uploadProgress.style.width = '0%';
            showToast(`Upload failed: ${error.message}`, 'error');
        }
    }

    function renderUploadedFiles() {
        if (uploadedFiles.length === 0) {
            uploadedFilesList.innerHTML = '<div class="empty-files-hint">No PDF documents attached</div>';
            return;
        }

        uploadedFilesList.innerHTML = uploadedFiles.map(f => `
            <div class="file-item">
                <div class="file-info">
                    <i class="fa-solid fa-file-pdf text-emerald"></i>
                    <span class="file-name" title="${f.name}">${f.name}</span>
                </div>
            </div>
        `).join('');
    }

    // --- Session History Management ---
    function startNewSession() {
        currentSessionId = generateUUID();
        localStorage.setItem('bioassistant_current_session', currentSessionId);
        chatMessages.innerHTML = '';
        welcomeHero.style.display = 'flex';
        activeSessionTitle.querySelector('span').textContent = 'Biology Research Assistant';
        showToast('New session started', 'info');
    }

    function clearCurrentChat() {
        chatMessages.innerHTML = '';
        welcomeHero.style.display = 'flex';
        showToast('Workspace cleared', 'info');
    }

    function renderSessionList() {
        if (sessions.length === 0) {
            sessionList.innerHTML = '<div class="empty-files-hint">No recent history</div>';
            return;
        }

        sessionList.innerHTML = sessions.map(s => `
            <div class="session-item ${s.id === currentSessionId ? 'active' : ''}" data-id="${s.id}">
                <div class="file-info">
                    <i class="fa-regular fa-message"></i>
                    <span class="session-title-text">${s.title}</span>
                </div>
                <button class="btn-delete-session" data-delete="${s.id}" title="Delete">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>
        `).join('');

        // Session Item Click Handlers
        document.querySelectorAll('.session-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.closest('.btn-delete-session')) return;
                const id = item.getAttribute('data-id');
                switchSession(id);
            });
        });

        document.querySelectorAll('.btn-delete-session').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = btn.getAttribute('data-delete');
                deleteSession(id);
            });
        });
    }

    function saveSessionTitle(title) {
        let existing = sessions.find(s => s.id === currentSessionId);
        if (existing) {
            existing.title = title;
        } else {
            sessions.unshift({ id: currentSessionId, title: title, timestamp: Date.now() });
        }
        localStorage.setItem('bioassistant_sessions', JSON.stringify(sessions));
        renderSessionList();
    }

    function switchSession(id) {
        currentSessionId = id;
        localStorage.setItem('bioassistant_current_session', currentSessionId);
        const session = sessions.find(s => s.id === id);
        if (session) {
            activeSessionTitle.querySelector('span').textContent = session.title;
        }
        renderSessionList();
    }

    function deleteSession(id) {
        sessions = sessions.filter(s => s.id !== id);
        localStorage.setItem('bioassistant_sessions', JSON.stringify(sessions));
        if (currentSessionId === id) {
            startNewSession();
        } else {
            renderSessionList();
        }
    }

    // --- Send Message to FastAPI Backend (/chat) ---
    async function handleSendMessage() {
        const query = chatInput.value.trim();
        if (!query) return;

        // Clear input and hide hero screen
        chatInput.value = '';
        chatInput.style.height = 'auto';
        welcomeHero.style.display = 'none';

        // Save session title if new
        const displayTitle = query.length > 30 ? query.substring(0, 30) + '...' : query;
        saveSessionTitle(displayTitle);
        activeSessionTitle.querySelector('span').textContent = displayTitle;

        // Append User Message to UI
        appendUserMessage(query);

        // Create Assistant Container
        const assistantRow = appendAssistantContainer();
        const statusCard = assistantRow.querySelector('.agent-status-card');
        const bubble = assistantRow.querySelector('.message-bubble-content');

        btnSend.disabled = true;

        try {
            statusCard.querySelector('.status-text').textContent = 'Analyzing request...';

            const response = await fetch(getApiUrl('/chat'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: query,
                    session_id: currentSessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            statusCard.remove();

            if (data.needs_input) {
                renderHITLCard(assistantRow, data.question);
            } else {
                const finalAnswer = data.answer || "No response received.";
                renderAssistantMarkdown(bubble, finalAnswer);
            }

        } catch (error) {
            statusCard.remove();
            bubble.innerHTML = `<div class="text-rose"><strong>Error:</strong> Unable to connect to server (${error.message}). Check backend connection.</div>`;
            showToast('API request failed.', 'error');
        } finally {
            btnSend.disabled = false;
            scrollToBottom();
        }
    }

    // --- Resume Interrupted State (/resume) ---
    async function handleResumeChoice(choice, assistantRow) {
        const statusCard = document.createElement('div');
        statusCard.className = 'agent-status-card';
        statusCard.innerHTML = `
            <div class="status-spinner"></div>
            <span class="status-text">Processing choice: "${choice}"...</span>
        `;

        const hitlCard = assistantRow.querySelector('.hitl-card');
        if (hitlCard) hitlCard.replaceWith(statusCard);

        try {
            const response = await fetch(getApiUrl('/resume'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    choice: choice
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            statusCard.remove();

            const bubble = assistantRow.querySelector('.message-bubble-content');

            if (data.needs_input) {
                renderHITLCard(assistantRow, data.question);
            } else {
                const finalAnswer = data.answer || "Completed.";
                renderAssistantMarkdown(bubble, finalAnswer);
            }

        } catch (error) {
            statusCard.remove();
            showToast(`Resume error: ${error.message}`, 'error');
        } finally {
            scrollToBottom();
        }
    }

    // --- UI Rendering Helpers ---
    function appendUserMessage(text) {
        const row = document.createElement('div');
        row.className = 'message-row user';
        row.innerHTML = `
            <div class="avatar user"><i class="fa-solid fa-user"></i></div>
            <div class="message-bubble">
                <p>${escapeHTML(text)}</p>
            </div>
        `;
        chatMessages.appendChild(row);
        scrollToBottom();
    }

    function appendAssistantContainer() {
        const row = document.createElement('div');
        row.className = 'message-row assistant';
        row.innerHTML = `
            <div class="avatar assistant"><i class="fa-solid fa-microscope"></i></div>
            <div class="message-bubble">
                <div class="agent-status-card">
                    <div class="status-spinner"></div>
                    <span class="status-text">Synthesizing response...</span>
                </div>
                <div class="message-bubble-content markdown-body"></div>
            </div>
        `;
        chatMessages.appendChild(row);
        scrollToBottom();
        return row;
    }

    function renderHITLCard(assistantRow, questionText) {
        const bubble = assistantRow.querySelector('.message-bubble');
        const hitlDiv = document.createElement('div');
        hitlDiv.className = 'hitl-card';
        hitlDiv.innerHTML = `
            <div class="hitl-header">
                <i class="fa-solid fa-circle-question"></i>
                <span>Action Required</span>
            </div>
            <div class="hitl-question">${escapeHTML(questionText || "Additional verification needed. How should the system proceed?")}</div>
            <div class="hitl-actions">
                <button class="hitl-btn" data-choice="web_search"><i class="fa-solid fa-globe"></i> Search Web</button>
                <button class="hitl-btn" data-choice="refine"><i class="fa-solid fa-arrows-rotate"></i> Refine Query</button>
                <button class="hitl-btn" data-choice="proceed"><i class="fa-solid fa-check"></i> Continue</button>
            </div>
            <div class="hitl-input-row">
                <input type="text" class="hitl-input" placeholder="Custom instructions...">
                <button class="btn-primary hitl-submit-custom">Submit</button>
            </div>
        `;

        bubble.appendChild(hitlDiv);

        hitlDiv.querySelectorAll('.hitl-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const choice = btn.getAttribute('data-choice');
                handleResumeChoice(choice, assistantRow);
            });
        });

        const customInput = hitlDiv.querySelector('.hitl-input');
        const submitCustomBtn = hitlDiv.querySelector('.hitl-submit-custom');
        submitCustomBtn.addEventListener('click', () => {
            const val = customInput.value.trim();
            if (val) handleResumeChoice(val, assistantRow);
        });
    }

    function renderAssistantMarkdown(container, rawMarkdown) {
        if (window.marked) {
            container.innerHTML = marked.parse(rawMarkdown);
        } else {
            container.textContent = rawMarkdown;
        }

        if (window.hljs) {
            container.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        }

        if (window.renderMathInElement) {
            try {
                renderMathInElement(container, {
                    delimiters: [
                        { left: '$$', right: '$$', display: true },
                        { left: '$', right: '$', display: false },
                        { left: '\\(', right: '\\)', display: false },
                        { left: '\\[', right: '\\]', display: true }
                    ],
                    throwOnError: false
                });
            } catch (e) {}
        }

        const actionRow = document.createElement('div');
        actionRow.className = 'message-actions';
        actionRow.innerHTML = `
            <button class="action-btn btn-copy" title="Copy Markdown"><i class="fa-regular fa-copy"></i> Copy</button>
            <button class="action-btn btn-download" title="Download Report"><i class="fa-solid fa-download"></i> Export .md</button>
        `;
        container.appendChild(actionRow);

        actionRow.querySelector('.btn-copy').addEventListener('click', () => {
            navigator.clipboard.writeText(rawMarkdown);
            showToast('Copied to clipboard.', 'success');
        });

        actionRow.querySelector('.btn-download').addEventListener('click', () => {
            downloadFile('Biology_Research_Report.md', rawMarkdown);
        });
    }

    function downloadFile(filename, text) {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/markdown;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    function escapeHTML(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function scrollToBottom() {
        const chatContainer = document.getElementById('chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
