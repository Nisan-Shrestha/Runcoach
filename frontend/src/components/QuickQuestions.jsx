import { useState, useEffect } from "react";
import { quickQuestionsAPI } from "../services/api";
import { Zap } from "lucide-react";

export default function QuickQuestions({ onQuestionClick }) {
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      const data = await quickQuestionsAPI.getQuestions();
      setQuestions(data.questions);
    } catch (error) {
      console.error("Error loading questions:", error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center gap-2 mb-3">
        <Zap className="w-5 h-5 text-secondary" />
        <h2 className="font-semibold text-lg">Quick Questions</h2>
      </div>
      <div className="space-y-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            className="w-full text-left px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-md transition text-sm"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
