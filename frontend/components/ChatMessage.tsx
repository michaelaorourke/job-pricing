import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User, Copy, CheckCircle } from 'lucide-react';
import { useState } from 'react';

interface ChatMessageProps {
  message: {
    id: string;
    content: string;
    sender: 'user' | 'assistant';
    timestamp: Date;
    isTyping?: boolean;
  };
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.sender === 'assistant';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Format message content with markdown-like styling
  const formatContent = (content: string) => {
    // Split by line breaks to handle formatting
    const lines = content.split('\n');

    return lines.map((line, idx) => {
      // Headers
      if (line.startsWith('**') && line.endsWith('**')) {
        return (
          <div key={idx} className="font-semibold text-gray-900 mt-3 mb-1">
            {line.replace(/\*\*/g, '')}
          </div>
        );
      }

      // Bullet points
      if (line.startsWith('• ') || line.startsWith('- ')) {
        return (
          <div key={idx} className="flex items-start gap-2 my-1">
            <span className="text-gray-500 mt-0.5">•</span>
            <span className="flex-1">{line.substring(2)}</span>
          </div>
        );
      }

      // Numbers/Salary formatting
      if (line.includes('$')) {
        return (
          <div key={idx} className="my-1 font-medium text-green-700">
            {line}
          </div>
        );
      }

      // Warning/Important text
      if (line.startsWith('⚠️') || line.startsWith('❌') || line.startsWith('✅')) {
        return (
          <div key={idx} className={`my-2 font-medium ${
            line.startsWith('⚠️') ? 'text-amber-600' :
            line.startsWith('❌') ? 'text-red-600' :
            'text-green-600'
          }`}>
            {line}
          </div>
        );
      }

      // Code blocks or special formatting
      if (line.startsWith('[') && line.endsWith(']')) {
        return (
          <div key={idx} className="px-3 py-2 rounded-lg my-2 font-mono text-sm bg-gray-100 text-gray-800">
            {line}
          </div>
        );
      }

      // Regular text
      if (line.trim()) {
        return <div key={idx} className="my-1">{line}</div>;
      }

      return <div key={idx} className="h-2" />;
    });
  };

  if (message.isTyping) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex gap-3 mb-4"
      >
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-blue-600" />
        </div>
        <div className="flex-1">
          <div className="inline-block px-4 py-3 rounded-2xl bg-gray-100">
            <div className="flex gap-1">
              <motion.div
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-2 h-2 rounded-full bg-gray-400"
              />
              <motion.div
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                className="w-2 h-2 rounded-full bg-gray-400"
              />
              <motion.div
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                className="w-2 h-2 rounded-full bg-gray-400"
              />
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 mb-4 ${isAssistant ? '' : 'flex-row-reverse'}`}
    >
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isAssistant ? 'bg-blue-100' : 'bg-green-100'
      }`}>
        {isAssistant ? (
          <Bot className="w-4 h-4 text-blue-600" />
        ) : (
          <User className="w-4 h-4 text-green-600" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isAssistant ? '' : 'flex justify-end'}`}>
        <div className={`group relative inline-block max-w-[85%]`}>
          <div
            className={`px-4 py-3 rounded-2xl ${
              isAssistant
                ? 'bg-gray-100 text-gray-800'
                : 'bg-blue-600 text-white'
            }`}
            style={{
              borderBottomLeftRadius: isAssistant ? '4px' : '16px',
              borderBottomRightRadius: isAssistant ? '16px' : '4px'
            }}
          >
            <div className="text-sm">
              {isAssistant ? formatContent(message.content) : message.content}
            </div>
          </div>

          {/* Copy button for assistant messages */}
          {isAssistant && (
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg bg-white/80 hover:bg-white"
              title="Copy message"
            >
              {copied ? (
                <CheckCircle className="w-3.5 h-3.5 text-green-600" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-gray-500" />
              )}
            </button>
          )}

          {/* Timestamp */}
          <div className={`text-xs text-gray-500 mt-1 ${isAssistant ? '' : 'text-right'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </motion.div>
  );
};