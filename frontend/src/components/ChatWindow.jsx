import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble.jsx';
import TypingIndicator from './TypingIndicator.jsx';
import HandoffCard from './HandoffCard.jsx';

export default function ChatWindow({ messages, isLoading, starterChips, onChipClick }) {
  const bottomRef = useRef(null);
  const containerRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  // Show welcome state when no messages
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="chat-window" ref={containerRef}>
        <div className="welcome-container">
          <div className="welcome-avatar" aria-hidden="true">💜</div>
          <h2 className="welcome-title">Hey, I'm TrustyCare</h2>
          <p className="welcome-text">
            I'm here to help you think through pre-marriage health screenings — 
            no pressure, no judgment, just a real conversation. What's on your mind?
          </p>
          <div className="welcome-chips" role="group" aria-label="Conversation starters">
            {starterChips.map((chip, i) => (
              <button
                key={i}
                className="welcome-chip"
                onClick={() => onChipClick(chip)}
                id={`starter-chip-${i}`}
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
        <div ref={bottomRef} />
      </div>
    );
  }

  return (
    <div className="chat-window" ref={containerRef} role="log" aria-live="polite">
      {messages.map((msg) => {
        // Render handoff card for handoff-triggered bot messages
        if (msg.role === 'bot' && msg.handoff_triggered) {
          return (
            <div key={msg.id}>
              <MessageBubble message={msg} />
              <div className="message-row bot" style={{ marginTop: '12px' }}>
                <div className="bot-avatar-small" aria-hidden="true">💜</div>
                <HandoffCard />
              </div>
            </div>
          );
        }

        return <MessageBubble key={msg.id} message={msg} />;
      })}

      {isLoading && <TypingIndicator />}

      <div ref={bottomRef} />
    </div>
  );
}
