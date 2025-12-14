import { useState } from "react";
import { UserProvider, useUserProfile } from "./context/UserContext";
import ProfileForm from "./components/ProfileForm";
import QuickQuestions from "./components/QuickQuestions";
import ChatContainer from "./components/ChatContainer";
import ChatInput from "./components/ChatInput";
import { chatAPI } from "./services/api";
import { RotateCcw } from "lucide-react";

function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const { userProfile } = useUserProfile();

  const handleSendMessage = async (message) => {
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(message, userProfile);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.response,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "❌ Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuestionClick = (question) => {
    const cleanQuestion = question.replace(/^[\u{1F300}-\u{1F9FF}]\s*/u, "");
    handleSendMessage(cleanQuestion);
  };

  const handleReset = async () => {
    if (window.confirm("Clear chat history?")) {
      try {
        await chatAPI.resetChat();
        setMessages([]);
      } catch (error) {
        console.error("Reset error:", error);
      }
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-80 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto">
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
            🏃 RunCoach AI
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Your personal running assistant
          </p>
        </div>

        <ProfileForm />
        <QuickQuestions onQuestionClick={handleQuestionClick} />

        {messages.length > 0 && (
          <button
            onClick={handleReset}
            className="w-full mt-4 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md flex items-center justify-center gap-2 text-sm transition"
          >
            <RotateCcw className="w-4 h-4" />
            Reset Chat
          </button>
        )}
      </div>

      <div className="flex-1 flex flex-col">
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-800">Chat</h2>
        </div>

        <ChatContainer messages={messages} />
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}

function App() {
  return (
    <UserProvider>
      <ChatApp />
    </UserProvider>
  );
}

export default App;
