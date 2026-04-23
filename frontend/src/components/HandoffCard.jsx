/**
 * HandoffCard — appears when the bot triggers advisor handoff.
 * Shows a warm card with CTA to book a free advisor call.
 * Rose gold accent, gradient background.
 */
export default function HandoffCard() {
  const handleBookClick = () => {
    // In production, this would open a booking flow or redirect
    window.open('https://trustycare.com', '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="handoff-card" id="handoff-card">
      <div className="handoff-icon" aria-hidden="true">🤝</div>
      <div className="handoff-title">Talk to a TrustyCare Advisor</div>
      <div className="handoff-subtitle">
        Free 20-min call · Real person · No pressure
      </div>
      <button
        className="handoff-cta"
        onClick={handleBookClick}
        id="handoff-cta-button"
      >
        Book now
        <span className="handoff-cta-icon" aria-hidden="true">→</span>
      </button>
    </div>
  );
}
