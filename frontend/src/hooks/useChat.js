import { useState, useCallback, useRef } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/chat';

/**
 * Custom hook for chat state management and API communication.
 *
 * Manages conversation history, loading state, and API calls
 * to the TrustyBot FastAPI backend.
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const conversationIdRef = useRef(crypto.randomUUID());

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text.trim(),
      timestamp: Date.now(),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Build conversation history for API
      const historyForApi = messages.map((m) => ({
        role: m.role === 'user' ? 'user' : 'bot',
        content: m.content,
      }));

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text.trim(),
          conversation_id: conversationIdRef.current,
          conversation_history: historyForApi,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        id: crypto.randomUUID(),
        role: 'bot',
        content: data.response,
        timestamp: Date.now(),
        category: data.category,
        handoff_triggered: data.handoff_triggered,
        sources: data.sources || [],
        quality_verdict: data.quality_verdict,
      };

      // Small delay to feel more natural (emotional pause for heavy topics)
      const delay = data.category === 'emotional_escalation' ? 1500 : 600;
      await new Promise((resolve) => setTimeout(resolve, delay));

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat API error:', error);

      const errorMessage = {
        id: crypto.randomUUID(),
        role: 'bot',
        content:
          "I'm having trouble connecting right now. Please make sure the backend server is running and try again.",
        timestamp: Date.now(),
        category: 'error',
        handoff_triggered: false,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, isLoading]);

  return {
    messages,
    isLoading,
    sendMessage,
    conversationId: conversationIdRef.current,
  };
}
