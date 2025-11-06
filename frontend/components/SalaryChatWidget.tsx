'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageCircle, X, Minimize2, Send, DollarSign,
  TrendingUp, MapPin, Briefcase, ArrowRight, FileText,
  Bell, ChevronDown, Upload
} from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import axios from 'axios';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  isTyping?: boolean;
}

interface JobAnalysis {
  id: string;
  job_title: string;
  location: string;
  level: number;
  years_experience_min: number;
  years_experience_max: number;
  skills_extracted: string[];
}

interface SalaryRange {
  recommended_min: string;
  recommended_target: string;
  recommended_max: string;
  confidence_score: string;
  market_insights: any;
}

interface SalaryChatWidgetProps {
  jobAnalysisId?: string;
  className?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const SalaryChatWidget: React.FC<SalaryChatWidgetProps> = ({
  jobAnalysisId,
  className = ""
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(null);
  const [salaryRange, setSalaryRange] = useState<SalaryRange | null>(null);
  const [hasNotification, setHasNotification] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize chat session
  useEffect(() => {
    if (jobAnalysisId && isOpen) {
      initializeChat();
    }
  }, [jobAnalysisId, isOpen]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, isMinimized]);

  const initializeChat = async () => {
    try {
      // Create chat session if we have a job analysis
      if (jobAnalysisId) {
        const sessionResponse = await axios.post(
          `${API_URL}/api/chat/session?job_id=${jobAnalysisId}`
        );
        setSessionId(sessionResponse.data.session_id);

        // Get job details
        const jobResponse = await axios.get(`${API_URL}/api/jobs/${jobAnalysisId}`);
        setJobAnalysis(jobResponse.data);

        // Get salary calculation
        const salaryResponse = await axios.post(
          `${API_URL}/api/analysis/calculate/${jobAnalysisId}`
        );
        setSalaryRange(salaryResponse.data);

        // Set initial greeting with job context
        const greeting = `Hello! I'm analyzing the **${jobResponse.data.job_title}** position in ${jobResponse.data.location}.

Based on my analysis:
• Level: ${jobResponse.data.detected_level} (${getLevelName(jobResponse.data.detected_level)})
• Experience: ${jobResponse.data.years_experience_min}-${jobResponse.data.years_experience_max} years
• Key Skills: ${jobResponse.data.skills_extracted.slice(0, 3).join(', ')}

**Recommended Salary Range:**
• Minimum: $${parseInt(salaryResponse.data.recommended_min).toLocaleString()}
• Target: $${parseInt(salaryResponse.data.recommended_target).toLocaleString()}
• Maximum: $${parseInt(salaryResponse.data.recommended_max).toLocaleString()}

How can I help you understand this compensation analysis?`;

        setMessages([{
          id: '1',
          content: greeting,
          sender: 'assistant',
          timestamp: new Date()
        }]);

        setHasNotification(true);
      } else {
        // No job analysis - generic greeting
        setMessages([{
          id: '1',
          content: 'Welcome to the Salary Intelligence Platform! Upload a job description to get started, or ask me any questions about compensation benchmarking.',
          sender: 'assistant',
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      console.error('Error initializing chat:', error);
      setMessages([{
        id: '1',
        content: 'Hello! I can help you analyze job descriptions and provide salary recommendations. How can I assist you today?',
        sender: 'assistant',
        timestamp: new Date()
      }]);
    }
  };

  const getLevelName = (level: number): string => {
    const levels: { [key: number]: string } = {
      1: 'Entry Level',
      2: 'Junior',
      3: 'Mid-Level',
      4: 'Experienced',
      5: 'Senior',
      6: 'Lead',
      7: 'Staff/Principal',
      8: 'Director',
      9: 'VP',
      10: 'C-Level'
    };
    return levels[level] || 'Unknown';
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Add typing indicator
    const typingMessage: Message = {
      id: 'typing',
      content: '',
      sender: 'assistant',
      timestamp: new Date(),
      isTyping: true
    };

    setMessages(prev => [...prev, typingMessage]);

    try {
      if (sessionId) {
        // Send message to backend
        const response = await axios.post(
          `${API_URL}/api/chat/message?session_id=${sessionId}`,
          { content: inputValue },
          { headers: { 'Content-Type': 'application/json' } }
        );

        // Remove typing and add response
        setMessages(prev => [
          ...prev.filter(m => m.id !== 'typing'),
          {
            id: Date.now().toString(),
            content: response.data.response,
            sender: 'assistant',
            timestamp: new Date()
          }
        ]);
      } else {
        // No session - provide generic response
        await new Promise(resolve => setTimeout(resolve, 1000));
        setMessages(prev => [
          ...prev.filter(m => m.id !== 'typing'),
          {
            id: Date.now().toString(),
            content: 'Please upload a job description first so I can provide specific salary recommendations.',
            sender: 'assistant',
            timestamp: new Date()
          }
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev.filter(m => m.id !== 'typing'),
        {
          id: Date.now().toString(),
          content: 'I apologize, but I encountered an error. Please try again.',
          sender: 'assistant',
          timestamp: new Date()
        }
      ]);
    }

    setIsTyping(false);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsTyping(true);
    setMessages(prev => [...prev, {
      id: 'upload',
      content: `Uploading and analyzing ${file.name}...`,
      sender: 'assistant',
      timestamp: new Date(),
      isTyping: true
    }]);

    try {
      const response = await axios.post(`${API_URL}/api/jobs/upload`, formData);

      // Initialize chat with the new job analysis
      window.location.href = `/?job=${response.data.id}`;
    } catch (error) {
      console.error('Error uploading file:', error);
      setMessages(prev => [
        ...prev.filter(m => m.id !== 'upload'),
        {
          id: Date.now().toString(),
          content: 'Failed to upload the file. Please ensure it\'s a valid PDF, DOCX, or text file.',
          sender: 'assistant',
          timestamp: new Date()
        }
      ]);
      setIsTyping(false);
    }
  };

  const handleQuickAction = (action: string) => {
    setInputValue(action);
    setTimeout(() => handleSend(), 100);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = jobAnalysis ? [
    'Explain the salary calculation',
    'Compare to market rates',
    'What skills affect the salary?',
    'Geographic adjustments?',
    'Total compensation package?'
  ] : [
    'How does salary benchmarking work?',
    'What factors affect compensation?',
    'Upload job description'
  ];

  return (
    <div className={className}>
      {/* Floating Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-blue-600 shadow-lg flex items-center justify-center z-50 text-white hover:bg-blue-700"
          >
            <MessageCircle className="w-6 h-6" />

            {/* Notification indicator */}
            {hasNotification && (
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"
              />
            )}
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className={`fixed bottom-6 right-6 w-96 rounded-2xl shadow-2xl z-50 bg-white border border-gray-200`}
            style={{
              height: isMinimized ? 'auto' : '600px',
              maxHeight: '80vh'
            }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 rounded-t-2xl bg-gradient-to-r from-blue-600 to-blue-700 text-white">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                  <DollarSign className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-semibold">Salary Intelligence Assistant</div>
                  <div className="text-xs opacity-90">
                    {jobAnalysis ? jobAnalysis.job_title : 'Ready to analyze'}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1">
                {salaryRange && (
                  <TrendingUp className="w-4 h-4 text-green-300" />
                )}
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <Minimize2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    setIsOpen(false);
                    setHasNotification(false);
                  }}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Chat Content */}
            {!isMinimized && (
              <>
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-4" style={{ height: 'calc(100% - 180px)' }}>
                  {messages.map(message => (
                    <ChatMessage key={message.id} message={message} />
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* Quick Actions */}
                <div className="px-4 pb-2">
                  <div className="flex gap-2 overflow-x-auto pb-2">
                    {quickActions.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleQuickAction(action)}
                        disabled={isTyping}
                        className="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200"
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Input Area */}
                <div className="border-t border-gray-200 px-4 py-3">
                  <div className="flex gap-2">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileUpload}
                      accept=".pdf,.docx,.txt"
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isTyping}
                      className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                      title="Upload job description"
                    >
                      <Upload className="w-5 h-5 text-gray-600" />
                    </button>

                    <textarea
                      ref={inputRef}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask about salary insights..."
                      disabled={isTyping}
                      rows={1}
                      className="flex-1 px-3 py-2 rounded-lg resize-none border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      style={{ maxHeight: '80px' }}
                    />
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleSend}
                      disabled={!inputValue.trim() || isTyping}
                      className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
                        inputValue.trim() && !isTyping
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-200 text-gray-400'
                      }`}
                    >
                      <Send className="w-4 h-4" />
                    </motion.button>
                  </div>

                  {/* Context indicator */}
                  {jobAnalysis && (
                    <div className="mt-2 text-xs text-gray-500 flex items-center gap-2">
                      <Briefcase className="w-3 h-3" />
                      {jobAnalysis.job_title}
                      <MapPin className="w-3 h-3 ml-2" />
                      {jobAnalysis.location}
                    </div>
                  )}
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SalaryChatWidget;