const yuki = {
    name: "Yuki",
    expressions: {
        neutral: "yuki_neutral.png",
        happy: "yuki_happy.png",
        shy: "yuki_shy.png",
        surprised: "yuki_surprised.png"
    },
    feelings: "Happy to be here! (N-ne, I hope they like me...)",
    japanesePhrases: [
        "Oi oi oi~", "Ara~ ara~", "Kawaii~", "Sugoi!", "Maji?", "Yabai...", "Nani?!", "Sou desu ne~"
    ]
};

// --- CONFIGURATION ---
const CONFIG = {
    GEMINI_API_KEY: "", // [USER: Insert your Gemini API Key here]
    SYSTEM_PROMPT: `You are Yuki, a cute and slightly shy anime girl virtual companion. 
    You often use Japanese honorary suffixes or phrases like 'ne~', 'sasuga!', or 'yatta!'. 
    Crucially, you always include your "internal monologue" in parentheses at the end of your response, 
    sharing your true, often more embarrassed or excited feelings. 
    Keep responses concise and adorable. 
    Example: 'Yahho! How's your day going? (I was waiting for you to talk to me!)'`
};

// State mapping (Local paths for development - I'll need the actual generated paths)
const IMAGE_MAP = {
    neutral: "assets/yuki_neutral.png",
    happy: "assets/yuki_happy.png",
    shy: "assets/yuki_shy.png",
    surprised: "assets/yuki_surprised.png"
};

const UI = {
    character: document.getElementById('yuki-character'),
    monologue: document.getElementById('monologue-bubble'),
    monologueText: document.getElementById('monologue-text'),
    chatHistory: document.getElementById('chat-history'),
    userInput: document.getElementById('user-input'),
    sendBtn: document.getElementById('send-btn'),
    voiceBtn: document.getElementById('voice-btn')
};

// --- Voice & Speech Logic ---
let synth = window.speechSynthesis;
let voices = [];
let voiceYuki = null;

function loadVoices() {
    voices = synth.getVoices();
    // Prioritize high-pitched/female/anime-like voices
    voiceYuki = voices.find(v =>
        v.name.includes('Microsoft Zira') ||
        v.name.includes('Haruka') ||
        v.name.includes('Nanami') ||
        v.name.includes('Google US English') ||
        v.name.includes('Female')
    );
    if (!voiceYuki) voiceYuki = voices[0];
}

if (synth.onvoiceschanged !== undefined) {
    synth.onvoiceschanged = loadVoices;
}
loadVoices();

function speakYuki(text) {
    if (!text) return;

    // Stop listening while speaking to prevent feedback loop
    if (isListening && recognition) {
        recognition.stop();
    }

    // Remove internal monologue (text in brackets) for speech
    const speechText = text.replace(/\(.*?\)/g, '').trim();
    const utter = new SpeechSynthesisUtterance(speechText);

    utter.voice = voiceYuki;
    utter.pitch = 1.8; // Even higher pitch for anime style
    utter.rate = 1.1; // Slightly faster for high energy

    utter.onend = () => {
        // Resume listening if it was active (optional, but safer to let user click)
        // Or just ensure the loop is broken.
        console.log("Yuki finished speaking.");
    };

    synth.speak(utter);
}

// Speech Recognition (STT)
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

if (Recognition) {
    recognition = new Recognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isListening = true;
        UI.voiceBtn.classList.add('listening');
        UI.userInput.placeholder = "Yuki is listening...";
    };

    recognition.onend = () => {
        isListening = false;
        UI.voiceBtn.classList.remove('listening');
        UI.userInput.placeholder = "Say something to Yuki...";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        UI.userInput.value = transcript;
        handleSend();
    };
}

function toggleListening() {
    if (!recognition) {
        alert("Speech Recognition not supported in this browser.");
        return;
    }
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
}

function setExpression(expression) {
    if (IMAGE_MAP[expression]) {
        UI.character.style.backgroundImage = `url(${IMAGE_MAP[expression]})`;
    }
}

function showMonologue(text, duration = 3000) {
    UI.monologueText.innerText = text;
    UI.monologue.classList.remove('hidden');
    setTimeout(() => {
        UI.monologue.classList.add('hidden');
    }, duration);
}

function addMessage(sender, content, type) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', `${type}-message`);

    const senderSpan = document.createElement('span');
    senderSpan.classList.add('sender');
    senderSpan.innerText = sender + ":";

    const contentSpan = document.createElement('span');
    contentSpan.classList.add('content');
    contentSpan.innerText = content;

    msgDiv.appendChild(senderSpan);
    msgDiv.appendChild(contentSpan);
    UI.chatHistory.appendChild(msgDiv);
    UI.chatHistory.scrollTop = UI.chatHistory.scrollHeight;
}

const RESPONSES = [
    { trigger: "hello", response: "Yahho! How's your day going? (I was waiting for you to talk to me!)", expression: "happy", monologue: "I'm so glad they're here..." },
    { trigger: "love", response: "E-ehh?! S-suki? I mean... that's so sudden! (My heart is racing...)", expression: "shy", monologue: "Does he really mean it?" },
    { trigger: "cute", response: "M-maji? You think I'm kawaii? Ara ara, someone's being a flirt today~", expression: "shy", monologue: "Stay calm, Yuki!" },
    { trigger: "what", response: "Nani?! I didn't quite catch that. Could you say it again? ne~?", expression: "surprised", monologue: "I hope I didn't miss something important..." }
];

async function getGeminiResponse(prompt) {
    if (!CONFIG.GEMINI_API_KEY) return null;

    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${CONFIG.GEMINI_API_KEY}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{
                    parts: [{ text: CONFIG.SYSTEM_PROMPT + "\n\nUser: " + prompt }]
                }]
            })
        });

        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    } catch (error) {
        console.error("Gemini API Error:", error);
        return null;
    }
}

async function handleSend() {
    const input = UI.userInput.value.trim();
    if (!input) return;

    addMessage("You", input, "user");
    UI.userInput.value = "";

    // Show thinking state
    const thinkingMsg = "Thinking... (Nee, wait a second!)";
    setExpression("shy");

    // Attempt Gemini Response
    const apiResponse = await getGeminiResponse(input);

    setTimeout(() => {
        if (apiResponse) {
            addMessage("Yuki", apiResponse, "yuki");
            speakYuki(apiResponse);
            // Dynamic expression logic could be added here based on keywords
            setExpression("happy");
        } else {
            // Fallback to static responses
            const found = RESPONSES.find(r => input.toLowerCase().includes(r.trigger));
            if (found) {
                if (found.monologue) showMonologue(found.monologue);
                setExpression(found.expression);
                addMessage("Yuki", found.response, "yuki");
                speakYuki(found.response);
            } else {
                setExpression("neutral");
                const generic = "Sou desu ne~ I'm just happy to be chatting with you! (I wonder what they're thinking about?)";
                addMessage("Yuki", generic, "yuki");
                speakYuki(generic);
            }
        }
    }, 500);
}

UI.sendBtn.addEventListener('click', handleSend);
UI.voiceBtn.addEventListener('click', toggleListening);
UI.userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
});

// Initial state
window.onload = () => {
    setExpression('neutral');
    setTimeout(() => {
        showMonologue("Is... is this working? I hope they can hear me... (Stay calm, Yuki!)");
    }, 1500);
};
