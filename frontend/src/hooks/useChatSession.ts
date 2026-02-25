import { useEffect, useRef, useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface SessionConfig {
  timeoutDuration?: number; // in milliseconds, default 30 minutes
  persistInSession?: boolean; // persist in sessionStorage, default true
}

interface SessionInfo {
  sessionId: string;
  startTime: Date;
  lastActivityTime: Date;
  isActive: boolean;
}

/**
 * Custom hook for managing chat session lifecycle
 * Handles session creation, timeout detection, and cleanup
 */
export const useChatSession = (config: SessionConfig = {}) => {
  const {
    timeoutDuration = 30 * 60 * 1000, // 30 minutes
    persistInSession = true,
  } = config;

  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isInitialized = useRef(false);

  /**
   * Start a new chat session
   */
  const startSession = useCallback(() => {
    const sessionId = uuidv4();
    const now = new Date();
    
    const newSession: SessionInfo = {
      sessionId,
      startTime: now,
      lastActivityTime: now,
      isActive: true,
    };

    setSessionInfo(newSession);

    // Persist in sessionStorage if enabled
    if (persistInSession) {
      sessionStorage.setItem('maxChatSession', JSON.stringify({
        sessionId,
        startTime: now.toISOString(),
        lastActivityTime: now.toISOString(),
      }));
    }

    console.log('🎯 Started new chat session:', sessionId);
    return sessionId;
  }, [persistInSession]);

  /**
   * End the current session
   */
  const endSession = useCallback(async () => {
    if (!sessionInfo || !sessionInfo.isActive) return;

    console.log('🔚 Ending chat session:', sessionInfo.sessionId);

    // Clear timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    // Mark session as inactive
    setSessionInfo(prev => prev ? { ...prev, isActive: false } : null);

    // Clean up sessionStorage
    if (persistInSession) {
      sessionStorage.removeItem('maxChatSession');
    }

    // TODO: Send session end event to backend
    try {
      // When implementing full backend integration, add API call here
      // await api.post('/max/session/end', { sessionId: sessionInfo.sessionId });
    } catch (error) {
      console.warn('Failed to notify backend of session end:', error);
    }
  }, [sessionInfo, persistInSession]);

  /**
   * Update session activity (called when user sends a message)
   */
  const updateActivity = useCallback(() => {
    if (!sessionInfo || !sessionInfo.isActive) return;

    const now = new Date();
    
    setSessionInfo(prev => prev ? {
      ...prev,
      lastActivityTime: now,
    } : null);

    // Update sessionStorage
    if (persistInSession) {
      const stored = sessionStorage.getItem('maxChatSession');
      if (stored) {
        const sessionData = JSON.parse(stored);
        sessionData.lastActivityTime = now.toISOString();
        sessionStorage.setItem('maxChatSession', JSON.stringify(sessionData));
      }
    }

    // Reset timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      console.log('⏰ Session timeout reached, ending session');
      endSession();
    }, timeoutDuration);

    console.log('🔄 Updated session activity');
  }, [sessionInfo, persistInSession, timeoutDuration, endSession]);

  /**
   * Initialize or restore session from sessionStorage
   */
  const initializeSession = useCallback(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    if (persistInSession) {
      const stored = sessionStorage.getItem('maxChatSession');
      if (stored) {
        try {
          const sessionData = JSON.parse(stored);
          const lastActivity = new Date(sessionData.lastActivityTime);
          const now = new Date();
          
          // Check if session has expired
          if (now.getTime() - lastActivity.getTime() < timeoutDuration) {
            // Restore active session
            const restoredSession: SessionInfo = {
              sessionId: sessionData.sessionId,
              startTime: new Date(sessionData.startTime),
              lastActivityTime: lastActivity,
              isActive: true,
            };
            
            setSessionInfo(restoredSession);
            
            // Set timeout for remaining time
            const remainingTime = timeoutDuration - (now.getTime() - lastActivity.getTime());
            timeoutRef.current = setTimeout(() => {
              console.log('⏰ Restored session timeout reached, ending session');
              endSession();
            }, remainingTime);
            
            console.log('🔄 Restored chat session:', sessionData.sessionId);
            return sessionData.sessionId;
          } else {
            // Expired session, clean up
            sessionStorage.removeItem('maxChatSession');
            console.log('🕐 Previous session expired, cleaned up');
          }
        } catch (error) {
          console.warn('Failed to restore session from storage:', error);
          sessionStorage.removeItem('maxChatSession');
        }
      }
    }

    return null;
  }, [persistInSession, timeoutDuration, endSession]);

  /**
   * Get or create active session ID
   */
  const getSessionId = useCallback(() => {
    // Try to initialize/restore first
    const restoredSessionId = initializeSession();
    if (restoredSessionId) return restoredSessionId;

    // If no active session, start new one
    if (!sessionInfo || !sessionInfo.isActive) {
      return startSession();
    }

    return sessionInfo.sessionId;
  }, [sessionInfo, initializeSession, startSession]);

  /**
   * Get session duration in minutes
   */
  const getSessionDuration = useCallback(() => {
    if (!sessionInfo) return 0;
    
    const endTime = sessionInfo.isActive ? new Date() : sessionInfo.lastActivityTime;
    return Math.round((endTime.getTime() - sessionInfo.startTime.getTime()) / (1000 * 60));
  }, [sessionInfo]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Handle page visibility change
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && sessionInfo?.isActive) {
        // Page is hidden, reduce timeout to 5 minutes
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = setTimeout(() => {
            console.log('⏰ Hidden page timeout reached, ending session');
            endSession();
          }, 5 * 60 * 1000); // 5 minutes
        }
      } else if (!document.hidden && sessionInfo?.isActive) {
        // Page is visible again, restore full timeout
        updateActivity();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [sessionInfo, endSession, updateActivity]);

  // Handle beforeunload to end session cleanly
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (sessionInfo?.isActive) {
        // Synchronously end session
        if (persistInSession) {
          sessionStorage.removeItem('maxChatSession');
        }
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [sessionInfo, persistInSession]);

  return {
    sessionInfo,
    sessionId: sessionInfo?.sessionId || null,
    isSessionActive: sessionInfo?.isActive || false,
    sessionDuration: getSessionDuration(),
    
    // Actions
    startSession,
    endSession,
    updateActivity,
    getSessionId,
    
    // Utilities
    getSessionDuration,
  };
};