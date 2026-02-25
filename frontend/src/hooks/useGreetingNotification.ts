import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import { getCurrentUser } from '@/lib/auth';
import api from '@/lib/api';
import { AxiosError } from 'axios';

interface UseGreetingNotificationReturn {
  showNotification: boolean;
  greetingMessage: string | null;
  loadingGreeting: boolean;
  handleNotificationClick: (openChat: () => void) => void;
  dismissNotification: () => void;
  resetGreeting: () => void;
}

export const useGreetingNotification = (): UseGreetingNotificationReturn => {
  const { isLoggedIn } = useAuth();
  const [showNotification, setShowNotification] = useState(false);
  const [greetingMessage, setGreetingMessage] = useState<string | null>(null);
  const [loadingGreeting, setLoadingGreeting] = useState(false);
  const [hasAttemptedFetch, setHasAttemptedFetch] = useState(false);

  const fetchGreeting = useCallback(async () => {
    if (!isLoggedIn || hasAttemptedFetch || loadingGreeting) return;
    
    try {
      setLoadingGreeting(true);
      const currentUser = getCurrentUser();
      if (!currentUser) return;

      const response = await api.post('/max/greeting', {
        user_id: String(currentUser.id),
        user_name: currentUser.first_name
          ? `${currentUser.first_name} ${currentUser.last_name || ""}`.trim()
          : undefined,
        session_id: crypto.randomUUID()
      });

      if (response.data && response.data.greeting_message) {
        setGreetingMessage(response.data.greeting_message);
        // Small delay to ensure UI is ready before showing notification
        setTimeout(() => {
          setShowNotification(true);
        }, 1000);
      }
    } catch (error) {
      if (error instanceof AxiosError) {
        console.error('Error fetching greeting:', error.response?.data?.detail || error.message);
      } else {
        console.error('Unexpected error fetching greeting:', error);
      }
    } finally {
      setLoadingGreeting(false);
      setHasAttemptedFetch(true);
    }
  }, [isLoggedIn, hasAttemptedFetch, loadingGreeting]);

  // Fetch greeting when user logs in
  useEffect(() => {
    if (isLoggedIn && !hasAttemptedFetch) {
      fetchGreeting();
    } else if (!isLoggedIn) {
      setShowNotification(false);
      setGreetingMessage(null);
      setHasAttemptedFetch(false);
      setLoadingGreeting(false);
    }
  }, [isLoggedIn, fetchGreeting, hasAttemptedFetch]);

  const handleNotificationClick = useCallback((openChat: () => void) => {
    setShowNotification(false);
    openChat();
  }, []);

  const dismissNotification = useCallback(() => {
    setShowNotification(false);
  }, []);

  const resetGreeting = useCallback(() => {
    setGreetingMessage(null);
    setHasAttemptedFetch(false);
    setShowNotification(false);
    setLoadingGreeting(false);
  }, []);

  return {
    showNotification,
    greetingMessage,
    loadingGreeting,
    handleNotificationClick,
    dismissNotification,
    resetGreeting,
  };
};

export default useGreetingNotification;