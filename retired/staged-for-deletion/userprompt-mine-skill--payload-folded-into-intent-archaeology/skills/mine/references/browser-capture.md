# Browser Capture — Tampermonkey Userscripts

## Overview

These Tampermonkey userscripts run in your browser and capture your prompts and model
responses in real-time from the web interfaces of OpenAI, Gemini, and Anthropic. This
eliminates the need to periodically download and parse data exports.

## Architecture

```
Browser (Tampermonkey)
    │
    ├── ChatGPT userscript ──→ capture conversation turns
    ├── Gemini userscript  ──→ capture conversation turns
    └── Claude.ai userscript ──→ capture conversation turns
    │
    ▼
Local API Server (prompt-mine web server)
    │
    ▼
SQLite Database (~/.prompt-mine/prompt_mine.db)
```

The userscripts POST captured data to a local API endpoint running on the prompt-mine
web server. The server handles deduplication, embedding generation, and storage.

## Prerequisites

1. **Tampermonkey extension** installed in your browser
2. **prompt-mine web server** running locally:
   ```bash
   python scripts/web_server.py --port 8420 --enable-capture-api
   ```
3. The capture API is at `http://localhost:8420/api/capture`

## API Endpoint

### POST /api/capture

```json
{
    "provider": "openai",
    "session_id": "browser-conv-1234567890",
    "session_title": "Help with Python sorting",
    "turns": [
        {
            "role": "user",
            "content_text": "How do I sort a list of dicts by a key in Python?",
            "model_id": null,
            "created_at": "2025-01-15T10:30:00Z"
        },
        {
            "role": "assistant",
            "content_text": "You can use the sorted() function with a key argument...",
            "model_id": "gpt-4",
            "created_at": "2025-01-15T10:30:05Z"
        }
    ]
}
```

**Response**: `201 Created` with `{"status": "ok", "turns_stored": 2}`

### GET /api/capture/status

Returns the server status and last capture timestamp.

## Tampermonkey Scripts

### chatgpt-capture.user.js

```javascript
// ==UserScript==
// @name         Prompt Mine — ChatGPT Capture
// @namespace    https://prompt-mine.dev
// @version      1.0.0
// @description  Capture ChatGPT conversations to Prompt Mine
// @match        https://chatgpt.com/*
// @match        https://chat.openai.com/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==

(function() {
    'use strict';

    const API_URL = 'http://localhost:8420/api/capture';
    let currentSessionId = null;
    let currentTurns = [];
    let debounceTimer = null;

    // Generate a stable session ID from the URL
    function getSessionId() {
        const match = window.location.pathname.match(/\/c\/([a-f0-9-]+)/);
        if (match) return `openai-browser-${match[1]}`;
        return `openai-browser-${Date.now()}`;
    }

    // Extract conversation title
    function getTitle() {
        const titleEl = document.querySelector('h1, [data-testid="conversation-title"]');
        return titleEl ? titleEl.textContent.trim() : 'Untitled';
    }

    // Extract all visible turns from the DOM
    function extractTurns() {
        const turns = [];
        const messages = document.querySelectorAll('[data-message-author-role], [class*="message"]');

        messages.forEach(msg => {
            // Detect role
            const roleAttr = msg.getAttribute('data-message-author-role');
            const isUser = roleAttr === 'user' ||
                           msg.closest('[data-testid*="user"]') !== null ||
                           msg.className.includes('user');
            const isAssistant = roleAttr === 'assistant' ||
                                msg.closest('[data-testid*="assistant"]') !== null ||
                                msg.className.includes('assistant');

            if (!isUser && !isAssistant) return;

            const content = msg.textContent?.trim();
            if (!content || content.length < 2) return;

            turns.push({
                role: isUser ? 'user' : 'assistant',
                content_text: content,
                model_id: isAssistant ? 'gpt-4' : null,
                created_at: new Date().toISOString()
            });
        });

        return turns;
    }

    // Send captured data to the API
    function sendCapture() {
        const sessionId = getSessionId();
        const turns = extractTurns();

        if (turns.length === 0) return;

        const payload = {
            provider: 'openai',
            session_id: sessionId,
            session_title: getTitle(),
            turns: turns
        };

        GM_xmlhttpRequest({
            method: 'POST',
            url: API_URL,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify(payload),
            onload: function(response) {
                if (response.status === 201) {
                    console.log('[Prompt Mine] Captured', turns.length, 'turns');
                } else {
                    console.warn('[Prompt Mine] Capture failed:', response.status);
                }
            },
            onerror: function(error) {
                console.error('[Prompt Mine] Capture error:', error);
            }
        });
    }

    // Observe DOM changes (ChatGPT uses React, content updates dynamically)
    const observer = new MutationObserver(function(mutations) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const newSessionId = getSessionId();
            if (newSessionId !== currentSessionId) {
                if (currentSessionId && currentTurns.length > 0) {
                    sendCapture();  // Flush previous session
                }
                currentSessionId = newSessionId;
                currentTurns = [];
            }
            extractTurns();
        }, 2000);  // Debounce: wait 2s after last DOM change
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    console.log('[Prompt Mine] ChatGPT capture active');
})();
```

### gemini-capture.user.js

```javascript
// ==UserScript==
// @name         Prompt Mine — Gemini Capture
// @namespace    https://prompt-mine.dev
// @version      1.0.0
// @description  Capture Google Gemini conversations to Prompt Mine
// @match        https://gemini.google.com/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==

(function() {
    'use strict';

    const API_URL = 'http://localhost:8420/api/capture';
    let debounceTimer = null;

    function getSessionId() {
        // Gemini uses URL fragments for conversation IDs
        const hash = window.location.hash;
        const match = hash.match(/\/([a-f0-9]+)/);
        if (match) return `gemini-browser-${match[1]}`;
        return `gemini-browser-${Date.now()}`;
    }

    function extractTurns() {
        const turns = [];
        // Gemini uses model-response and user-query selectors
        const userQueries = document.querySelectorAll('query-content, .user-query-bubble');
        const modelResponses = document.querySelectorAll('model-response, .model-response-bubble');

        // Interleave user and model turns based on DOM order
        const allMessages = document.querySelectorAll(
            'query-content, model-response, .user-query-bubble, .model-response-bubble'
        );

        allMessages.forEach(msg => {
            const isUser = msg.tagName === 'QUERY-CONTENT' ||
                           msg.className.includes('user-query');
            const text = msg.textContent?.trim();
            if (!text || text.length < 2) return;

            turns.push({
                role: isUser ? 'user' : 'assistant',
                content_text: text,
                model_id: isUser ? null : 'gemini-1.5-pro',
                created_at: new Date().toISOString()
            });
        });

        return turns;
    }

    function sendCapture() {
        const turns = extractTurns();
        if (turns.length === 0) return;

        GM_xmlhttpRequest({
            method: 'POST',
            url: API_URL,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify({
                provider: 'gemini',
                session_id: getSessionId(),
                session_title: 'Gemini Conversation',
                turns: turns
            }),
            onload: (res) => {
                if (res.status === 201) {
                    console.log('[Prompt Mine] Captured', turns.length, 'Gemini turns');
                }
            }
        });
    }

    const observer = new MutationObserver(() => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(sendCapture, 3000);
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    console.log('[Prompt Mine] Gemini capture active');
})();
```

### claude-ai-capture.user.js

```javascript
// ==UserScript==
// @name         Prompt Mine — Claude.ai Capture
// @namespace    https://prompt-mine.dev
// @version      1.0.0
// @description  Capture Claude.ai web conversations to Prompt Mine
// @match        https://claude.ai/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==

(function() {
    'use strict';

    const API_URL = 'http://localhost:8420/api/capture';
    let debounceTimer = null;

    function getSessionId() {
        const match = window.location.pathname.match(/\/chat\/([a-f0-9-]+)/);
        if (match) return `anthropic-browser-${match[1]}`;
        return `anthropic-browser-${Date.now()}`;
    }

    function extractTurns() {
        const turns = [];
        // Claude.ai uses human-turn and assistant-turn classes
        const allTurns = document.querySelectorAll(
            '[data-testid*="turn"], .human-turn, .assistant-turn, [class*="HumanMessage"], [class*="AssistantMessage"]'
        );

        allTurns.forEach(turn => {
            const isUser = turn.className.includes('human') ||
                           turn.className.includes('Human') ||
                           turn.getAttribute('data-testid')?.includes('human');
            const text = turn.textContent?.trim();
            if (!text || text.length < 2) return;

            turns.push({
                role: isUser ? 'user' : 'assistant',
                content_text: text,
                model_id: isUser ? null : 'claude-sonnet-4-20250514',
                created_at: new Date().toISOString()
            });
        });

        return turns;
    }

    function sendCapture() {
        const turns = extractTurns();
        if (turns.length === 0) return;

        GM_xmlhttpRequest({
            method: 'POST',
            url: API_URL,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify({
                provider: 'anthropic',
                session_id: getSessionId(),
                session_title: 'Claude.ai Conversation',
                turns: turns
            }),
            onload: (res) => {
                if (res.status === 201) {
                    console.log('[Prompt Mine] Captured', turns.length, 'Claude.ai turns');
                }
            }
        });
    }

    const observer = new MutationObserver(() => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(sendCapture, 3000);
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    console.log('[Prompt Mine] Claude.ai capture active');
})();
```

## Installation Instructions

1. Install [Tampermonkey](https://www.tampermonkey.net/) browser extension
2. Start the prompt-mine web server with capture API enabled:
   ```bash
   python scripts/web_server.py --port 8420 --enable-capture-api
   ```
3. Create a new userscript in Tampermonkey for each provider you use
4. Paste the appropriate script content and save
5. Navigate to the provider's web interface — the console should show
   `[Prompt Mine] ... capture active`
6. Use the chat interface normally; turns are captured automatically

## Limitations

- **DOM-based extraction** is fragile: Provider UI changes may break selectors.
  Check for updates when this happens.
- **No streaming capture**: Turn content is captured after the response is fully
  rendered (the debounce delay handles this).
- **Rate limiting**: The capture API deduplicates by session_id + turn_index, so
  repeated captures of the same conversation are idempotent.
- **Content Security Policy**: Some providers may block localhost requests. If this
  happens, use `@grant GM_xmlhttpRequest` (already included) which bypasses CSP.
