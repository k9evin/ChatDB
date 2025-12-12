import { useEffect, useRef, useState, useCallback } from "react";

interface WebSocketMessage {
  type: "token" | "tool_start" | "tool_result" | "complete" | "error";
  content?: string;
  tool?: string;
  output?: any;
  thread_id?: string;
}

interface UseWebSocketOptions {
  url?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
  autoConnect?: boolean;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    url = "ws://localhost:8000/ws/chat",
    onMessage,
    onError,
    onOpen,
    onClose,
    autoConnect = true,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const hasLoggedError = useRef(false);

  const connect = useCallback(() => {
    // Prevent multiple simultaneous connection attempts
    if (wsRef.current?.readyState === WebSocket.OPEN || isConnecting) {
      return;
    }

    // Clean up any existing connection before creating a new one
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch (e) {
        // Ignore errors when closing
      }
      wsRef.current = null;
    }

    setIsConnecting(true);
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttempts.current = 0;
        hasLoggedError.current = false; // Reset error logging on successful connection
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          onMessage?.(data);
        } catch (error) {
          // Only log parsing errors once to prevent spam
          if (!hasLoggedError.current) {
            console.error("Error parsing WebSocket message:", error);
            hasLoggedError.current = true;
          }
        }
      };

      ws.onerror = (error) => {
        setIsConnecting(false);
        // Only call onError callback on first error to prevent spam
        if (!hasLoggedError.current) {
          hasLoggedError.current = true;
          onError?.(error);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setIsConnecting(false);
        onClose?.();

        // Attempt to reconnect only if autoConnect is enabled
        if (autoConnect && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 1000 * reconnectAttempts.current); // Exponential backoff
        }
      };

      wsRef.current = ws;
    } catch (error) {
      setIsConnecting(false);
      // Only log creation errors once to prevent spam
      if (!hasLoggedError.current) {
        console.error("Error creating WebSocket:", error);
        hasLoggedError.current = true;
        onError?.(error as Event);
      }
    }
  }, [url, onMessage, onError, onOpen, onClose, isConnecting]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  const sendMessage = useCallback((message: string, databaseUrl?: string, threadId?: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const payload: { message: string; database_url?: string; thread_id?: string } = { message };
      if (databaseUrl) {
        payload.database_url = databaseUrl;
      }
      if (threadId) {
        payload.thread_id = threadId;
      }
      wsRef.current.send(JSON.stringify(payload));
      return true;
    }
    return false;
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoConnect]); // Only depend on autoConnect to prevent reconnection loops

  return {
    isConnected,
    isConnecting,
    connect,
    disconnect,
    sendMessage,
  };
}
