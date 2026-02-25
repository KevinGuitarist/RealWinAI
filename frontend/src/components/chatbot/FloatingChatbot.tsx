import React, { useState, useEffect, useCallback, useRef } from "react";
import { Drawer, DrawerTrigger, DrawerContent } from "@/components/ui/drawer";
import { Button } from "@/components/ui/button";
import { MessageCircle, RotateCcw, Loader2 } from "lucide-react";
import { getCurrentUser } from "@/lib/auth";
import { useGreetingNotification } from "@/hooks/useGreetingNotification";
import { useChatSession } from "@/hooks/useChatSession";
import GreetingNotification from "./GreetingNotification";
import api from "@/lib/api";
import { AxiosError } from "axios";

interface ChatMessage {
  type: "user" | "bot";
  content: string;
}

const FloatingChatbot: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const hasShownInitialGreeting = useRef(false);

  // Session management hook
  const {
    sessionId,
    isSessionActive,
    sessionDuration,
    getSessionId,
    updateActivity,
    endSession,
  } = useChatSession({
    timeoutDuration: 30 * 60 * 1000, // 30 minutes
    persistInSession: true,
  });

  // Greeting notification system
  const {
    showNotification,
    greetingMessage,
    loadingGreeting,
    handleNotificationClick,
    dismissNotification,
    resetGreeting,
  } = useGreetingNotification();

  // Ref for the messages container to enable auto-scroll
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Function to scroll to bottom of chat
  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior: "smooth",
        block: "end",
        inline: "nearest",
      });
    }
  }, []);

  // Auto-scroll when messages change
  useEffect(() => {
    if (messages.length > 0) {
      // Small delay to ensure DOM has updated
      setTimeout(scrollToBottom, 100);
    }
  }, [messages, scrollToBottom]);

  // Auto-scroll when loading state changes
  useEffect(() => {
    if (loading) {
      setTimeout(scrollToBottom, 100);
    }
  }, [loading, scrollToBottom]);

  // Session management integrated with chat lifecycle
  useEffect(() => {
    if (open && messages.length > 0) {
      // Update session activity when chat is opened and has messages
      updateActivity();
    }
  }, [open, messages.length, updateActivity]);

  const handleClearChat = async () => {
    // End current session before clearing
    if (isSessionActive) {
      await endSession();
    }

    setMessages([]);
    resetGreeting(); // Reset the greeting system
    hasShownInitialGreeting.current = false; // Reset greeting flag

    // After clearing, the useEffect will automatically fetch a new greeting
  };

  // Handle opening chat from notification
  const openChatWithGreeting = useCallback(() => {
    setOpen(true);
    // The greeting will be shown by the useEffect when the drawer opens
  }, []);

  // Handle drawer open/close state changes
  const handleOpenChange = useCallback((isOpen: boolean) => {
    setOpen(isOpen);
    // Reset greeting flag when chat is closed so new greeting can be fetched next time
    if (!isOpen) {
      hasShownInitialGreeting.current = false;
    }
  }, []);

  // Show greeting when chat opens and no messages exist
  useEffect(() => {
    if (
      open &&
      messages.length === 0 &&
      !hasShownInitialGreeting.current &&
      greetingMessage
    ) {
      hasShownInitialGreeting.current = true;
      setMessages([{ type: "bot", content: greetingMessage }]);
      updateActivity(); // Update session activity when showing greeting
    }
  }, [open, messages.length, greetingMessage, updateActivity]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }

    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput(""); // Clear input immediately
    setMessages((prev) => [...prev, { type: "user", content: userMessage }]);
    setLoading(true);

    // Get or create session ID and update activity
    const currentSessionId = getSessionId();
    updateActivity(); // Update session activity when user sends message

    // Prepare payload for backend
    const user = getCurrentUser();
    const payload = {
      user_id: user?.id ? String(user.id) : "anonymous",
      message: userMessage,
      user_name: user?.first_name
        ? `${user.first_name} ${user.last_name || ""}`.trim()
        : undefined,
      session_id: currentSessionId,
    };

    try {
      // Use extended timeout for chatbot requests as they involve complex AI processing
      const response = await api.post("/max/web/chat", payload, {
        timeout: 60000, // 60 seconds for AI processing
      });
      const botReply = response.data?.response || "No response from AI.";
      setMessages((prev) => [...prev, { type: "bot", content: botReply }]);
    } catch (error) {
      console.error("Chatbot API error:", error);

      let errorMessage =
        "Sorry, there was an error connecting to the AI service.";

      if (error instanceof AxiosError) {
        if (error.code === "ECONNABORTED") {
          // Timeout error
          errorMessage =
            "The AI is taking longer than usual to respond. This might be due to complex processing. Please try a simpler question or try again later.";
        } else if (error.response) {
          // Server responded with error status
          const status = error.response.status;
          if (status === 401 || status === 403) {
            errorMessage = "Please log in to use the chatbot.";
          } else if (status === 429) {
            errorMessage =
              "Too many requests. Please wait a moment and try again.";
          } else if (status === 500) {
            errorMessage = "Server error. Please try again later.";
          } else {
            errorMessage = `Service error (${status}). Please try again.`;
          }
        } else if (error.request) {
          // Network error
          errorMessage =
            "Unable to connect to the service. Please check your internet connection.";
        }
      }

      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          content: errorMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Greeting Notification */}
      {showNotification && greetingMessage && (
        <GreetingNotification
          greeting={greetingMessage}
          onNotificationClick={() => {
            handleNotificationClick(() => openChatWithGreeting());
          }}
          onClose={dismissNotification}
        />
      )}

      <Drawer
        open={open}
        onOpenChange={handleOpenChange}
        shouldScaleBackground={true}
      >
        <DrawerTrigger asChild>
          <Button
            variant="ghost"
            className="fixed bottom-4 right-4 z-50 bg-transparent hover:bg-transparent p-0 w-24 h-32 sm:w-32 sm:h-40 border-0 shadow-none group transition-all duration-300 hover:scale-110"
            aria-label="Open MAX Chatbot"
          >
            <div className="relative w-full h-full flex items-end justify-center overflow-visible">
              {/* Outermost ambient glow - most subtle with soft edges */}
              <div
                className="absolute inset-0 rounded-full animate-ambient-glow opacity-30 group-hover:opacity-50 transition-opacity duration-300"
                style={{
                  transform: "scale(1.8)",
                  filter: "blur(20px)",
                  background:
                    "radial-gradient(circle, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.08) 30%, rgba(34, 197, 94, 0.04) 60%, rgba(34, 197, 94, 0.01) 80%, transparent 100%)",
                }}
              ></div>

              {/* Middle glow layer - medium intensity with gradient softening */}
              <div
                className="absolute inset-0 rounded-full animate-glow-pulse opacity-40 group-hover:opacity-60 transition-opacity duration-300"
                style={{
                  transform: "scale(1.4)",
                  filter: "blur(14px)",
                  background:
                    "radial-gradient(circle, rgba(34, 197, 94, 0.25) 0%, rgba(34, 197, 94, 0.18) 25%, rgba(34, 197, 94, 0.12) 45%, rgba(34, 197, 94, 0.06) 65%, rgba(34, 197, 94, 0.02) 80%, transparent 100%)",
                }}
              ></div>

              {/* Inner glow layer - most focused with soft falloff */}
              <div
                className="absolute inset-0 rounded-full animate-pulse-glow opacity-50 group-hover:opacity-70 transition-opacity duration-300"
                style={{
                  transform: "scale(1.2)",
                  filter: "blur(10px)",
                  background:
                    "radial-gradient(circle, rgba(34, 197, 94, 0.4) 0%, rgba(34, 197, 94, 0.3) 20%, rgba(34, 197, 94, 0.2) 35%, rgba(34, 197, 94, 0.12) 50%, rgba(34, 197, 94, 0.06) 65%, rgba(34, 197, 94, 0.02) 80%, transparent 100%)",
                }}
              ></div>

              {/* Additional ultra-soft outer glow for maximum softening */}
              <div
                className="absolute inset-0 rounded-full animate-ambient-glow opacity-20 group-hover:opacity-35 transition-opacity duration-300"
                style={{
                  transform: "scale(2.2)",
                  filter: "blur(25px)",
                  background:
                    "radial-gradient(circle, rgba(34, 197, 94, 0.08) 0%, rgba(34, 197, 94, 0.04) 25%, rgba(34, 197, 94, 0.02) 50%, rgba(34, 197, 94, 0.005) 70%, transparent 100%)",
                }}
              ></div>

              {/* Floor shadow with breathing animation - Primary shadow */}
              <div
                className="absolute bottom-0 left-1/2 w-20 h-6 sm:w-24 sm:h-7 rounded-full animate-breathe-shadow"
                style={{
                  background:
                    "radial-gradient(ellipse, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.5) 40%, rgba(0, 0, 0, 0.2) 70%, transparent 100%)",
                  filter: "blur(2px)",
                  zIndex: 1,
                }}
              ></div>

              {/* Secondary sharper shadow for definition */}
              <div
                className="absolute bottom-0 left-1/2 w-16 h-4 sm:w-20 sm:h-5 rounded-full animate-breathe-shadow"
                style={{
                  background:
                    "radial-gradient(ellipse, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.3) 60%, transparent 80%)",
                  filter: "blur(1px)",
                  transform: "translateX(-50%) translateY(6px)",
                  zIndex: 2,
                }}
              ></div>

              {/* MAX Avatar with enhanced styling and floating animation */}
              <img
                src="/Max-Full.png"
                alt="MAX"
                className="relative w-full h-full object-contain transition-all duration-500 group-hover:scale-105 animate-float"
                style={{
                  filter:
                    "drop-shadow(0 6px 12px rgba(0, 0, 0, 0.15)) drop-shadow(0 0 20px rgba(34, 197, 94, 0.1))",
                  zIndex: 10,
                }}
              />

              {/* Subtle rim light effect on hover */}
              <div
                className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-30 transition-opacity duration-500 pointer-events-none"
                style={{
                  background:
                    "radial-gradient(circle, transparent 60%, rgba(34, 197, 94, 0.3) 80%, transparent 100%)",
                  filter: "blur(1px)",
                }}
              ></div>
            </div>
          </Button>
        </DrawerTrigger>
        <DrawerContent className="max-w-full w-full sm:w-[400px] ml-auto mr-0 h-[70vh] flex flex-col p-0">
          <div className="flex flex-col h-full w-full">
            {/* Header */}
            <div className="flex items-center justify-between px-4 pt-4 pb-2 border-b border-border">
              <div className="flex items-center gap-3">
                <img
                  src="/MAX-icon.png"
                  alt="MAX"
                  className="w-6 h-8 object-contain"
                />
                <div className="flex flex-col">
                  <span className="font-semibold text-lg text-foreground">
                    MAX
                  </span>
                  {isSessionActive && sessionDuration > 0 && (
                    <span className="text-xs text-muted-foreground">
                      Session: {sessionDuration}m
                    </span>
                  )}
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearChat}
                className="h-8 w-8 p-0 hover:bg-surface"
                title="Start fresh chat"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
            {/* Messages */}
            <div
              ref={messagesContainerRef}
              className="flex-1 overflow-y-auto px-4 py-2 space-y-2 bg-surface chatbot-scrollbar"
              style={{
                scrollbarWidth: "thin",
                scrollbarColor: "rgba(0, 0, 0, 0.3) transparent",
              }}
            >
              {/* Render messages */}
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    msg.type === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                      msg.type === "user"
                        ? "bg-brand-primary text-background rounded-br-sm"
                        : "bg-card text-foreground rounded-bl-sm"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {(loadingGreeting ||
                (open && messages.length === 0 && !greetingMessage)) && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-lg px-3 py-2 text-sm bg-card text-foreground rounded-bl-sm opacity-70 flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="italic">
                      MAX is preparing a personalized greeting...
                    </span>
                  </div>
                </div>
              )}
              {loading && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-lg px-3 py-2 text-sm bg-card text-foreground rounded-bl-sm opacity-70">
                    <span className="italic">
                      Analyzing your question and processing with AI... This may
                      take up to a minute.
                    </span>
                  </div>
                </div>
              )}
              {/* Invisible div to scroll to */}
              <div ref={messagesEndRef} />
            </div>
            {/* Input */}
            <form
              className="flex gap-2 p-4 border-t border-border bg-background"
              onSubmit={handleSendMessage}
            >
              <input
                className="flex-1 rounded-md border border-input bg-surface px-3 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={loading}
                autoComplete="off"
              />
              <Button
                type="submit"
                className="bg-brand-primary hover:bg-brand-primary-hover text-background px-4 transition-colors duration-200"
                disabled={loading || !input.trim()}
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Send"
                )}
              </Button>
            </form>
          </div>
        </DrawerContent>
      </Drawer>
    </>
  );
};

export default FloatingChatbot;
