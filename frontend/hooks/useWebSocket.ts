import { useCallback, useEffect, useRef, useState } from "react";
import config from "@/config";

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

// Helper function to convert HTTP/HTTPS URL to WebSocket URL
function getWebSocketUrl(
  backendUrl: string,
  path: string = "/ws/chat"
): string {
  const wsUrl = backendUrl
    .replace(/^http:\/\//, "ws://")
    .replace(/^https:\/\//, "wss://");
  return `${wsUrl}${path}`;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    url = getWebSocketUrl(config.backendUrl),
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
  const isFirstConnection = useRef(true); // Track if this is the first connection

  const onMessageRef = useRef(onMessage);
  const onErrorRef = useRef(onError);
  const onOpenRef = useRef(onOpen);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    onMessageRef.current = onMessage;
    onErrorRef.current = onError;
    onOpenRef.current = onOpen;
    onCloseRef.current = onClose;
  });

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
        hasLoggedError.current = false;
        onOpenRef.current?.();
      };

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          onMessageRef.current?.(data);
        } catch (error) {
          if (!hasLoggedError.current) {
            console.error("Error parsing WebSocket message:", error);
            hasLoggedError.current = true;
          }
        }
      };

      ws.onerror = (error) => {
        setIsConnecting(false);
        if (!hasLoggedError.current) {
          hasLoggedError.current = true;
          onErrorRef.current?.(error);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setIsConnecting(false);
        onCloseRef.current?.();

        if (autoConnect && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 1000 * reconnectAttempts.current);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      setIsConnecting(false);
      if (!hasLoggedError.current) {
        console.error("Error creating WebSocket:", error);
        hasLoggedError.current = true;
        onErrorRef.current?.(error as Event);
      }
    }
  }, [url, isConnecting, autoConnect]);

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

  const sendMessage = useCallback(
    (message: string, databaseUrl?: string, threadId?: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        const payload: {
          message: string;
          database_url?: string;
          thread_id?: string;
        } = { message };
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
    },
    []
  );

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
