"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Bot, Send, User } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/hooks/use-auth";
import api from "@/lib/api";
import axios, { AxiosInstance } from "axios";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string | null;
}

interface MessageResponse {
  id: number;
  conversation_id: number;
  role: "user" | "assistant";
  content: string;
  tool_calls: string | null;
  created_at: string;
}

// Create a separate API instance for chat to avoid double prefixing
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";
const chatApi: AxiosInstance = axios.create({
  baseURL: API_URL ? `${API_URL}` : "",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Add auth interceptor to chat API instance
chatApi.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor with error handling
chatApi.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors with clear messages
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;

      if (status === 401) {
        // Clear invalid token and redirect to login
        if (typeof window !== "undefined") {
          localStorage.removeItem("auth_token");
        }
        // Optionally redirect to login - we'll just return the error for the component to handle
        const message = typeof data?.detail === "string" ? data.detail : "Invalid or expired session. Please log in again.";
        return Promise.reject(new Error(message));
      }

      if (status === 400) {
        let message = "Validation error.";
        if (typeof data?.detail === "string") {
          message = data.detail;
        } else if (Array.isArray(data?.detail)) {
          message = data.detail.map((d: any) => d.msg || "Validation error").join(", ");
        }
        return Promise.reject(new Error(message));
      }

      if (status === 404) {
        return Promise.reject(new Error("Resource not found."));
      }

      const message = typeof data?.detail === "string" ? data.detail : `Request failed (${status})`;
      return Promise.reject(new Error(message));
    }

    if (error.code === "ECONNABORTED") {
      return Promise.reject(new Error("Request timed out. Please try again."));
    }

    return Promise.reject(new Error("Unable to connect to the server. Please check your connection."));
  }
);

export default function ChatPage() {
  const { user, token, isAuthenticated, isLoading: authIsLoading } = useAuth();
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations when component mounts
  useEffect(() => {
    if (!isAuthenticated || !user) return;

    const loadConversations = async () => {
      try {
        if (!user) {
        throw new Error('User not authenticated');
      }
      const response = await chatApi.get(`/api/${user.id}/conversations`);
        setConversations(response.data);

        // Auto-select the most recent conversation if available
        if (response.data.length > 0) {
          const latestConversation = response.data[0];
          setSelectedConversation(latestConversation.id);
          setConversationId(latestConversation.id);

          // Load messages for the selected conversation
          loadConversationMessages(latestConversation.id);
        }
      } catch (error: any) {
        console.error("Error loading conversations:", error);

        // Check if the error message indicates authentication issue
        if (error.message && (error.message.includes("Invalid or expired session") || error.message.includes("Unauthorized access"))) {
          toast.error("Session expired. Please log in again.");
          window.location.href = "/login";
        }
      }
    };

    loadConversations();
  }, [isAuthenticated, user]);

  // Load messages for a specific conversation
  const loadConversationMessages = async (convId: number) => {
    try {
      if (!user) {
        throw new Error('User not authenticated');
      }
      const response = await chatApi.get(`/api/${user.id}/conversations/${convId}/messages`);

      const formattedMessages: Message[] = response.data.map((msg: MessageResponse) => ({
        id: msg.id.toString(),
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));

      setMessages(formattedMessages);
    } catch (error: any) {
      console.error("Error loading conversation messages:", error);

      // Check if the error message indicates authentication issue
      if (error.message && (error.message.includes("Invalid or expired session") || error.message.includes("Unauthorized access"))) {
        toast.error("Session expired. Please log in again.");
        window.location.href = "/login";
      }
    }
  };

  // Handle conversation selection
  const handleSelectConversation = (convId: number) => {
    setSelectedConversation(convId);
    setConversationId(convId);
    loadConversationMessages(convId);
  };

  // Create new conversation
  const handleNewConversation = () => {
    setConversationId(null);
    setSelectedConversation(null);
    setMessages([]);
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading || !isAuthenticated || !user) return;

    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Use the separate chat API instance to avoid double prefixing of /api
      // Backend expects /api/{user.id}/chat, so we include /api in the path
      const requestBody: any = {
        message: inputValue,
      };

      // Include conversation ID if we have one
      if (conversationId !== null) {
        requestBody.conversation_id = conversationId;
      }

      if (!user) {
        throw new Error('User not authenticated');
      }
      const response = await chatApi.post(`/api/${user.id}/chat`, requestBody);

      const data = response.data;

      // Update conversation ID if it's the first message
      if (conversationId === null) {
        setConversationId(data.conversation_id);
      }

      // Add assistant message to chat
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error("Error sending message:", error);

      // Check if the error message indicates authentication issue
      if (error.message && (error.message.includes("Invalid or expired session") || error.message.includes("Unauthorized access"))) {
        toast.error("Session expired. Please log in again.");
        // Optionally redirect to login
        window.location.href = "/login";
      } else if (error.response?.status === 401) {
        toast.error("Session expired. Please log in again.");
        // Optionally redirect to login
        window.location.href = "/login";
      } else {
        toast.error("Failed to send message. Please try again.");
      }

      // Add error message to chat
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Check if user is loaded and redirect if not authenticated
  useEffect(() => {
    if (!authIsLoading && !isAuthenticated) {
      window.location.href = "/login";
    }
  }, [isAuthenticated, authIsLoading]);

  if (authIsLoading || !isAuthenticated || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <Card className="shadow-lg">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Bot className="h-6 w-6" />
              <CardTitle>AI Task Assistant</CardTitle>
            </div>
            <Button variant="outline" onClick={handleNewConversation}>
              + New Chat
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            Chat with our AI assistant to manage your tasks
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            {/* Conversation List Sidebar */}
            <div className="w-full md:w-64 flex-shrink-0">
              <h3 className="font-semibold mb-2">Conversations</h3>
              <ScrollArea className="h-[400px] pr-4">
                <div className="space-y-2">
                  {conversations.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No conversations yet</p>
                  ) : (
                    conversations.map((conv) => (
                      <Button
                        key={conv.id}
                        variant={selectedConversation === conv.id ? "secondary" : "ghost"}
                        className="w-full justify-start text-left h-auto py-2 px-3"
                        onClick={() => handleSelectConversation(conv.id)}
                      >
                        <span className="truncate">
                          {conv.created_at ? new Date(conv.created_at).toLocaleDateString() : "Untitled"}
                        </span>
                      </Button>
                    ))
                  )}
                </div>
              </ScrollArea>
            </div>

            {/* Chat Area */}
            <div className="flex-1">
              <ScrollArea className="h-[400px] w-full pr-4 mb-4">
                <div className="space-y-4">
                  {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground py-12">
                      <Bot className="h-12 w-12 mb-4" />
                      <h3 className="text-lg font-medium">Welcome to AI Task Assistant!</h3>
                      <p className="mt-2">
                        You can ask me to add, list, update, complete, or delete tasks.
                        <br />
                        Try: "Add buy groceries" or "Show me all my tasks"
                      </p>
                    </div>
                  ) : (
                    messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex items-start gap-3 ${
                          message.role === "user" ? "justify-end" : "justify-start"
                        }`}
                      >
                        {message.role === "assistant" && (
                          <Avatar className="h-8 w-8 mt-1">
                            <AvatarImage src="/placeholder-avatar.jpg" alt="AI Assistant" />
                            <AvatarFallback>
                              <Bot className="h-4 w-4" />
                            </AvatarFallback>
                          </Avatar>
                        )}
                        <div
                          className={`rounded-lg px-4 py-2 max-w-[80%] ${
                            message.role === "user"
                              ? "bg-primary text-primary-foreground ml-auto"
                              : "bg-muted"
                          }`}
                        >
                          <p>{message.content}</p>
                        </div>
                        {message.role === "user" && (
                          <Avatar className="h-8 w-8 mt-1">
                            <AvatarImage
                              src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || 'User')}&background=random`}
                              alt={user?.name || user?.email || "User"}
                            />
                            <AvatarFallback>
                              <User className="h-4 w-4" />
                            </AvatarFallback>
                          </Avatar>
                        )}
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Type your message here..."
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </form>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}