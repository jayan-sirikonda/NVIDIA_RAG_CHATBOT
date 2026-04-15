"use client";
import { useState, useRef, useEffect } from "react";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I am the Georgia Tech RAG Chatbot powered by NVIDIA NIM. Ask me anything about GA Tech."
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    const backendUrl = "http://localhost:8000/api/v1/chat/";

    try {
      const response = await fetch(backendUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [...messages, userMsg].map(m => ({role: m.role, content: m.content})) })
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      const assistantMsgId = (Date.now() + 1).toString();
      setMessages(prev => [...prev, { id: assistantMsgId, role: "assistant", content: "" }]);

      let assistantContent = "";
      
      while (reader) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        assistantContent += text;
        
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMsgId ? { ...msg, content: assistantContent } : msg
          )
        );
      }
    } catch (error) {
      console.error("Error fetching response:", error);
      setMessages(prev => [
        ...prev, 
        { id: Date.now().toString(), role: "assistant", content: "Error connecting to the server. Please ensure the backend is running." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="container">
      <header className="header">
        <h1>Georgia Tech AI Directory</h1>
        <p>Powered by NVIDIA NIM & Vector Search</p>
      </header>

      <div className="chat-box">
        <div className="message-list">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.role}`}>
              {msg.content ? (
                msg.content.split('\n').map((line, i) => (
                  <span key={i}>
                    {line}
                    <br />
                  </span>
                ))
              ) : (
                isLoading && msg.role === "assistant" && (
                  <div className="loading-dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                )
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form className="input-area" onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about Georgia Tech..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </main>
  );
}
