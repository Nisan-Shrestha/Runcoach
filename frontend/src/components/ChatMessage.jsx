import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Bot, User, ChevronDown, ChevronRight, Brain } from "lucide-react";

/**
 * Parse response to extract thinking and main content
 */
function parseResponse(text) {
  if (!text) return { thinking: null, content: "" };

  // Match <thinking>...</thinking> blocks
  const thinkingMatch = text.match(/<thinking>([\s\S]*?)<\/thinking>/i);

  // Extract thinking content
  const thinking = thinkingMatch ? thinkingMatch[1].trim() : null;

  // Remove thinking tags from main content
  let content = text.replace(/<thinking>[\s\S]*?<\/thinking>/gi, "");

  // Also handle unclosed thinking tags
  content = content.replace(/<thinking>[\s\S]*$/gi, "");

  // Clean up extra whitespace
  content = content.replace(/\n{3,}/g, "\n\n").trim();

  return { thinking, content };
}

function ThinkingSection({ thinking }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!thinking) return null;

  return (
    <div className="mb-2 ml-11">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 transition-colors"
      >
        {isOpen ? (
          <ChevronDown className="w-3.5 h-3.5" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5" />
        )}
        <Brain className="w-3.5 h-3.5" />
        <span>Thinking</span>
      </button>

      {isOpen && (
        <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-gray-600 italic">
          {thinking}
        </div>
      )}
    </div>
  );
}

export default function ChatMessage({ message, isUser }) {
  // Parse thinking and content for AI messages
  const { thinking, content } = isUser
    ? { thinking: null, content: message }
    : parseResponse(message);

  return (
    <div className="mb-4">
      {/* Thinking section (only for AI, shown above bubble) */}
      {!isUser && <ThinkingSection thinking={thinking} />}

      {/* Main message */}
      <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? "bg-primary" : "bg-gray-300"
          }`}
        >
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <Bot className="w-5 h-5 text-gray-700" />
          )}
        </div>

        <div
          className={`max-w-[70%] rounded-lg px-4 py-3 ${
            isUser ? "bg-primary text-white" : "bg-gray-100 text-gray-800"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{content}</p>
          ) : (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
