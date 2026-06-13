/**
 * JanKalyan — Chat UI Logic
 * Handles message sending, typing indicators, and language selection.
 */

(function () {
    "use strict";

    // DOM elements
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const sendBtn = document.getElementById("send-btn");
    const btnReset = document.getElementById("btn-reset");
    const langSelect = document.getElementById("lang-select");
    const welcomeCard = document.getElementById("welcome-card");
    const inputHint = document.getElementById("input-hint-text");

    // State
    let userId = "web_" + Math.random().toString(36).substring(2, 10);
    let isWaiting = false;
    let hasStarted = false;

    // ---- Language badge clicks on welcome card ----
    document.querySelectorAll(".lang-badge").forEach((badge) => {
        badge.addEventListener("click", () => {
            const lang = badge.dataset.lang;
            langSelect.value = lang;

            // Send greeting in selected language
            const greetings = { en: "Hi", hi: "नमस्ते", ta: "வணக்கம்" };
            sendMessage(greetings[lang] || "Hi");
        });
    });

    // ---- Send message ----
    function sendMessage(text) {
        text = text || messageInput.value.trim();
        if (!text || isWaiting) return;

        // Hide welcome card on first message
        if (!hasStarted) {
            hasStarted = true;
            if (welcomeCard) {
                welcomeCard.style.display = "none";
            }
            inputHint.innerHTML = 'Type <strong>reset</strong> to start over';
        }

        // Add user bubble
        addMessage(text, "user");
        messageInput.value = "";
        messageInput.focus();

        // Show typing indicator
        isWaiting = true;
        sendBtn.disabled = true;
        const typingEl = showTypingIndicator();

        // Send to backend
        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, message: text }),
        })
            .then((res) => res.json())
            .then((data) => {
                removeTypingIndicator(typingEl);
                addMessage(data.reply, "bot");
                isWaiting = false;
                sendBtn.disabled = false;
            })
            .catch((err) => {
                removeTypingIndicator(typingEl);
                addMessage(
                    "⚠️ Connection error. Please try again.",
                    "bot"
                );
                isWaiting = false;
                sendBtn.disabled = false;
                console.error("Chat error:", err);
            });
    }

    // ---- Add message bubble ----
    function addMessage(text, role) {
        const wrapper = document.createElement("div");
        wrapper.className = `message ${role}`;

        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.textContent = role === "bot" ? "🏛️" : "👤";

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";

        // Simple formatting: bold (*text*) and links
        let formatted = escapeHtml(text);
        // Bold: *text* → <strong>text</strong>
        formatted = formatted.replace(/\*([^*]+)\*/g, "<strong>$1</strong>");
        // URLs → clickable links
        formatted = formatted.replace(
            /(https?:\/\/[^\s<]+)/g,
            '<a href="$1" target="_blank" rel="noopener" style="color: var(--accent-light); text-decoration: underline;">$1</a>'
        );

        bubble.innerHTML = formatted;

        wrapper.appendChild(avatar);
        wrapper.appendChild(bubble);
        chatMessages.appendChild(wrapper);

        scrollToBottom();
    }

    // ---- Typing indicator ----
    function showTypingIndicator() {
        const wrapper = document.createElement("div");
        wrapper.className = "typing-indicator";
        wrapper.id = "typing-indicator";

        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.style.background = "linear-gradient(135deg, var(--accent), #d97706)";
        avatar.textContent = "🏛️";

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;

        wrapper.appendChild(avatar);
        wrapper.appendChild(bubble);
        chatMessages.appendChild(wrapper);

        scrollToBottom();
        return wrapper;
    }

    function removeTypingIndicator(el) {
        if (el && el.parentNode) {
            el.parentNode.removeChild(el);
        }
    }

    // ---- Helpers ----
    function scrollToBottom() {
        requestAnimationFrame(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // ---- Event listeners ----
    sendBtn.addEventListener("click", () => sendMessage());

    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    btnReset.addEventListener("click", () => {
        // Reset on backend
        fetch(`/api/reset/${userId}`, { method: "POST" });

        // Reset UI
        userId = "web_" + Math.random().toString(36).substring(2, 10);
        hasStarted = false;
        chatMessages.innerHTML = "";

        // Re-add welcome card
        chatMessages.innerHTML = `
            <div class="welcome-card" id="welcome-card">
                <div class="welcome-icon">🇮🇳</div>
                <h2>Find Your Government Schemes</h2>
                <p>Answer a few simple questions to discover welfare schemes you may be eligible for.</p>
                <div class="welcome-langs">
                    <span class="lang-badge" data-lang="en">English</span>
                    <span class="lang-badge" data-lang="hi">हिन्दी</span>
                    <span class="lang-badge" data-lang="ta">தமிழ்</span>
                </div>
                <div class="welcome-schemes">
                    <span class="scheme-tag">PM-KISAN</span>
                    <span class="scheme-tag">Ayushman Bharat</span>
                    <span class="scheme-tag">PMAY</span>
                    <span class="scheme-tag">Ujjwala</span>
                    <span class="scheme-tag">MGNREGA</span>
                    <span class="scheme-tag">+5 more</span>
                </div>
            </div>
        `;

        // Re-bind lang badges
        chatMessages.querySelectorAll(".lang-badge").forEach((badge) => {
            badge.addEventListener("click", () => {
                const lang = badge.dataset.lang;
                langSelect.value = lang;
                const greetings = { en: "Hi", hi: "नमस्ते", ta: "வணக்கம்" };
                sendMessage(greetings[lang] || "Hi");
            });
        });

        inputHint.innerHTML =
            'Say <strong>hi</strong>, <strong>नमस्ते</strong>, or <strong>வணக்கம்</strong> to start';
    });

    // Focus input on load
    messageInput.focus();
})();
