import React, { useState, useEffect, useCallback } from "react";
import { X, MessageCircle } from "lucide-react";

interface GreetingNotificationProps {
  greeting: string;
  onNotificationClick: () => void;
  onClose: () => void;
}

export const GreetingNotification: React.FC<GreetingNotificationProps> = ({
  greeting,
  onNotificationClick,
  onClose,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  // Show notification when greeting is available
  useEffect(() => {
    if (greeting) {
      setIsVisible(true);
    }
  }, [greeting]);

  const handleNotificationClick = () => {
    onNotificationClick();
    handleClose();
  };

  const handleClose = useCallback(() => {
    setIsVisible(false);
    setTimeout(() => {
      onClose();
    }, 300); // Wait for animation to complete
  }, [onClose]);

  // Auto-hide notification after 15 seconds
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        handleClose();
      }, 15000);

      return () => clearTimeout(timer);
    }
  }, [isVisible, handleClose]);

  if (!greeting) {
    return null;
  }

  return (
    <>
      {isVisible && (
        <div
          className={`fixed top-4 right-4 z-[60] max-w-sm w-full transition-all duration-300 ease-out ${
            isVisible
              ? "opacity-100 translate-y-0 scale-100"
              : "opacity-0 -translate-y-5 scale-95"
          }`}
        >
          <div className="bg-card border border-border rounded-lg shadow-lg p-4 cursor-pointer hover:bg-muted/50 transition-colors duration-200 group">
            {/* Header */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <img
                    src="/MAX-icon.png"
                    alt="MAX"
                    className="w-6 h-8 object-contain"
                  />
                  {/* Notification indicator */}
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                </div>
                <div>
                  <h4 className="font-medium text-sm text-foreground">
                    M.A.X.
                  </h4>
                  <p className="text-xs text-muted-foreground">Just now</p>
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleClose();
                }}
                className="text-muted-foreground hover:text-foreground transition-colors duration-200 p-1 hover:bg-muted rounded"
                aria-label="Close notification"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Message content */}
            <div onClick={handleNotificationClick} className="space-y-2">
              <p className="text-sm text-foreground leading-relaxed line-clamp-3">
                {greeting}
              </p>

              {/* Action hint */}
              <div className="flex items-center gap-1 text-xs text-muted-foreground group-hover:text-foreground transition-colors duration-200">
                <MessageCircle className="w-3 h-3" />
                <span>Click to open chat</span>
              </div>
            </div>

            {/* Subtle glow effect */}
            <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-green-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          </div>
        </div>
      )}
    </>
  );
};

export default GreetingNotification;
