/**
 * MessageBubble — renders a single chat message.
 * Supports types: bot, user, refusal (medical question).
 * Bot messages get an avatar; user messages are right-aligned.
 */
export default function MessageBubble({ message }) {
  const { role, content, category } = message;
  const isBot = role === 'bot';
  const isRefusal = isBot && category === 'medical_question';

  return (
    <div className={`message-row ${isBot ? 'bot' : 'user'}`}>
      {isBot && (
        <div className="bot-avatar-small" aria-hidden="true">💜</div>
      )}

      <div
        className={`message-bubble ${isBot ? 'bot' : 'user'} ${isRefusal ? 'refusal' : ''}`}
        id={`msg-${message.id}`}
      >
        {isRefusal && (
          <div className="refusal-badge">
            <span className="refusal-badge-icon">🩺</span>
            Medical question → Advisor
          </div>
        )}
        <div>{content}</div>
      </div>
    </div>
  );
}
