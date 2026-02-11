document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chatbot-toggle");
    const closeBtn = document.getElementById("chatbot-close");
    const chatWindow = document.getElementById("chatbot-window");
    const messages = document.getElementById("chatbot-messages");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");
    const sendBtn = document.querySelector(".chatbot-send");
    const INTRO_MESSAGE = "hello, iam lyra how can i help you";
    const conversation = [{ role: "assistant", content: INTRO_MESSAGE }];

    if (!toggleBtn || !chatWindow || !form) {
        return;
    }

    const openChat = () => {
        chatWindow.classList.add("open");
        input?.focus();
    };

    const closeChat = () => {
        chatWindow.classList.remove("open");
    };

    const toggleChat = () => {
        if (chatWindow.classList.contains("open")) {
            closeChat();
        } else {
            openChat();
        }
    };

    const scrollToBottom = () => {
        if (messages) {
            messages.scrollTop = messages.scrollHeight;
        }
    };

    const appendMessage = (author, text) => {
        if (!messages) return;

        const wrapper = document.createElement("div");
        wrapper.className = `chatbot-message ${author}`;

        const bubble = document.createElement("div");
        bubble.className = "chatbot-bubble";
        bubble.textContent = text;

        wrapper.appendChild(bubble);
        messages.appendChild(wrapper);
        scrollToBottom();
    };

    const sendMessage = async (text) => {
        appendMessage("user", text);
        const history = conversation.concat([{ role: "user", content: text }]);
        sendBtn.disabled = true;

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: text, history })
            });

            if (!response.ok) {
                throw new Error("Server error");
            }

            const data = await response.json();
            const reply = data.reply || "I'm still learning that.";
            appendMessage("bot", reply);
            conversation.push({ role: "user", content: text });
            conversation.push({ role: "assistant", content: reply });
        } catch (error) {
            appendMessage("bot", "Hmm, I couldn't reach the server. Try again in a moment.");
        } finally {
            sendBtn.disabled = false;
        }
    };

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        if (!chatWindow.classList.contains("open")) {
            openChat();
        }
        sendMessage(text);
    });

    toggleBtn.addEventListener("click", toggleChat);
    closeBtn?.addEventListener("click", closeChat);
});
