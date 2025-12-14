import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";

export default function ChatContainer({ messages }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">
              🏃 Welcome to RunCoach AI!
            </h2>
            <p>Ask me anything about running, nutrition, or training plans.</p>
            <p className="text-sm mt-2">
              Try the quick questions on the left to get started! 👈
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg, index) => (
            <ChatMessage
              key={index}
              message={msg.content}
              isUser={msg.role === "user"}
            />
          ))}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}
