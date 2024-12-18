document.getElementById('location-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch('', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('location-results').innerHTML = html;
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('chat-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const loadingMessage = document.getElementById('loading-message');
    loadingMessage.style.display = 'flex';

    const formData = new FormData(this);
    fetch('', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const chatContainer = document.getElementById('chat-container');
        let userMessage = document.createElement('div');
        userMessage.classList.add('chat-message', 'user');
        userMessage.innerHTML = `<div class="chat-bubble">${formData.get('query')}</div><div class="avatar">U</div>`;
        chatContainer.appendChild(userMessage);

        let aiMessage = document.createElement('div');
        aiMessage.classList.add('chat-message');
        aiMessage.innerHTML = `<div class="avatar">A</div><div class="chat-bubble"></div>`;
        chatContainer.appendChild(aiMessage);

        const chatBubble = aiMessage.querySelector('.chat-bubble');

        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    loadingMessage.style.display = 'none';
                    return;
                }
                chatBubble.textContent += decoder.decode(value, { stream: true });
                readStream();
            });
        }
        readStream();
    })
    .catch(error => {
        console.error('Error:', error);
        loadingMessage.style.display = 'none';
    });
});

document.getElementById('reset-chat').addEventListener('click', function() {
    fetch('/reset-chat', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(() => {
        document.getElementById('chat-container').innerHTML = '';
    })
    .catch(error => console.error('Error:', error));
});

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('collapsed');
}