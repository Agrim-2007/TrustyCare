import { useState } from 'react';
import ChatWindow from './components/ChatWindow.jsx';
import { useChat } from './hooks/useChat.js';

const STARTER_CHIPS = [
  "My family will never agree to this",
  "What if the results are bad?",
  "How does the assessment work?",
  "This feels like I don't trust them",
];

export default function App() {
  const {
    messages,
    isLoading,
    sendMessage,
    conversationId,
  } = useChat();

  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    const trimmed = inputValue.trim();
    if (!trimmed || isLoading) return;
    sendMessage(trimmed);
    setInputValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChipClick = (text) => {
    if (isLoading) return;
    sendMessage(text);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-avatar" aria-hidden="true">💜</div>
          <div className="header-info">
            <h1 className="header-title">TrustyCare</h1>
            <div className="header-status">
              <span className="status-dot" aria-hidden="true"></span>
              <span className="header-subtitle">Your health companion</span>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Window */}
      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        starterChips={STARTER_CHIPS}
        onChipClick={handleChipClick}
      />

      {/* Input Bar */}
      <div className="input-container">
        <div className="input-bar">
          <input
            id="chat-input"
            className="input-field"
            type="text"
            placeholder="Type your thoughts here..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            autoComplete="off"
            aria-label="Chat message input"
          />
          <button
            id="send-button"
            className="send-button"
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            aria-label="Send message"
          >
            ➜
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="powered-by">
        Powered by <a href="https://trustycare.com" target="_blank" rel="noopener noreferrer">TrustyCare</a>
      </div>
    </div>
  );
}
