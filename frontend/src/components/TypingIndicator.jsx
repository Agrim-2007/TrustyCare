/**
 * TypingIndicator — 3-dot pulse animation.
 * Styled as a bot bubble to maintain visual consistency.
 * Shown while waiting for API response.
 */
export default function TypingIndicator() {
  return (
    <div className="typing-row" role="status" aria-label="TrustyCare is typing">
      <div className="bot-avatar-small" aria-hidden="true">💜</div>
      <div className="typing-bubble">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  );
}
