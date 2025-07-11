// Chatbot FAQ/manual frontend
(function() {
    const toggle = document.getElementById('chatbot-toggle');
    const box = document.getElementById('chatbot-box');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const messages = document.getElementById('chatbot-messages');

    // Toggle chatbox
    toggle.onclick = function() {
        box.style.display = (box.style.display === 'none' || box.style.display === '') ? 'block' : 'none';
        if (box.style.display === 'block') {
            input.focus();
        }
    };

    // Add message to chat
    function addMessage(text, sender) {
        const msg = document.createElement('div');
        msg.className = 'chatbot-msg chatbot-' + sender;
        msg.style.margin = '8px 0';
        msg.style.textAlign = sender === 'user' ? 'right' : 'left';
        msg.innerHTML = `<span style="display:inline-block;padding:8px 14px;border-radius:16px;max-width:80%;background:${sender==='user'?'#007bff;color:#fff':'#eee;color:#222'};">${text}</span>`;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

    // Handle form submit
    form.onsubmit = function(e) {
        e.preventDefault();
        const question = input.value.trim();
        if (!question) return;
        addMessage(question, 'user');
        input.value = '';
        addMessage('<i>Sedang memproses...</i>', 'bot');
        // AJAX ke endpoint /chatbot/
        fetch('/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ question })
        })
        .then(res => res.json())
        .then(data => {
            // Hapus "Sedang memproses..."
            const loading = messages.querySelector('.chatbot-bot:last-child');
            if (loading && loading.innerHTML.includes('Sedang memproses')) loading.remove();
            addMessage(data.answer || 'Maaf, tidak ada jawaban.', 'bot');
        })
        .catch(() => {
            const loading = messages.querySelector('.chatbot-bot:last-child');
            if (loading && loading.innerHTML.includes('Sedang memproses')) loading.remove();
            addMessage('Terjadi kesalahan. Coba lagi.', 'bot');
        });
    };

    // CSRF helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
})();
