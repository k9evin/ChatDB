"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useToast } from "@/components/ui/use-toast";
import config from "@/config";
import { useDatabase } from "@/contexts/database-context";
import type { Message } from "./useConversation";
import { useWebSocket } from "./useWebSocket";

interface ChartData {
  chart_type: string;
  data: any[];
  vega_lite_spec?: any;
  config: {
    x_key?: string;
    y_key?: string;
    data_key?: string;
    value_key?: string;
    title?: string;
    x_label?: string;
    y_label?: string;
    multiple_series?: string[];
  };
}

interface UseChatProps {
  onPersistConversation: (
    messages: Message[],
    id?: string | null,
    skipRefresh?: boolean
  ) => Promise<void>;
  conversationId: string | null;
}

export function useChat({
  onPersistConversation,
  conversationId,
}: UseChatProps) {
  const { databaseUrl } = useDatabase();
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentAssistantMessage, setCurrentAssistantMessage] = useState("");
  const [toolCalls, setToolCalls] = useState<string[]>([]);
  const [pendingChartData, setPendingChartData] = useState<ChartData | null>(
    null
  );
  const [pendingTableData, setPendingTableData] = useState<any[] | null>(null);

  // Use refs to store latest values for use in callbacks
  const currentMessageRef = useRef("");
  const pendingChartRef = useRef<ChartData | null>(null);
  const pendingTableRef = useRef<any[] | null>(null);
  const conversationIdRef = useRef<string | null>(null);

  // Keep refs in sync with state
  useEffect(() => {
    currentMessageRef.current = currentAssistantMessage;
  }, [currentAssistantMessage]);

  useEffect(() => {
    pendingChartRef.current = pendingChartData;
  }, [pendingChartData]);

  useEffect(() => {
    pendingTableRef.current = pendingTableData;
  }, [pendingTableData]);

  useEffect(() => {
    conversationIdRef.current = conversationId;
  }, [conversationId]);

  const { isConnected, sendMessage, isConnecting } = useWebSocket({
    onMessage: (wsMessage) => {
      if (wsMessage.type === "token") {
        // Append token to current assistant message
        setCurrentAssistantMessage((prev) => prev + (wsMessage.content || ""));
      } else if (wsMessage.type === "tool_start") {
        // Track tool usage
        const toolName = wsMessage.tool || "unknown";
        setToolCalls((prev) => [...prev, toolName]);
      } else if (wsMessage.type === "tool_result") {
        // Tool execution completed
        console.log(
          "[WebSocket] Tool result:",
          wsMessage.tool,
          wsMessage.output
        );

        // Parse tool output - backend sends ToolMessage with content as JSON string
        let output = wsMessage.output || {};

        // If output has a content field with JSON string, parse it
        if (output.content && typeof output.content === "string") {
          try {
            output = JSON.parse(output.content);
            console.log("[WebSocket] Parsed output:", output);
          } catch (e) {
            console.warn(
              "[WebSocket] Failed to parse output.content as JSON:",
              e
            );
          }
        }

        // Check if this is a chart suggestion or execution result
        if (wsMessage.tool === "suggest_chart_type") {
          console.log("[WebSocket] suggest_chart_type output:", output);
          if (
            output.should_visualize &&
            output.chart_type &&
            output.chart_type !== "table"
          ) {
            // Store chart data for when message completes
            const chartData = {
              chart_type: output.chart_type,
              data: output.data || [],
              config: output.chart_config || {},
            };
            console.log(
              "[WebSocket] Setting pending chart data from suggest_chart_type:",
              chartData
            );
            // IMPORTANT: update ref immediately to avoid race with `complete`
            pendingChartRef.current = chartData;
            setPendingChartData(chartData);
          }
        } else if (wsMessage.tool === "prepare_chart_data") {
          console.log("[WebSocket] prepare_chart_data output:", output);
          if (output.chart_type && output.chart_type !== "table") {
            // Store prepared chart data (this is the final chart data ready for visualization)
            const chartData = {
              chart_type: output.chart_type,
              data: output.data || [],
              config: output.config || {},
              vega_lite_spec: output.vega_lite_spec || undefined,
            };
            console.log(
              "[WebSocket] Setting pending chart data from prepare_chart_data:",
              chartData
            );
            // IMPORTANT: update ref immediately to avoid race with `complete`
            pendingChartRef.current = chartData;
            setPendingChartData(chartData);
          }
        } else if (wsMessage.tool === "execute_sql_query" && output?.rows) {
          // Store table data (rows might be in output directly or in output.rows)
          const rows = output.rows || [];
          pendingTableRef.current = rows;
          setPendingTableData(rows);
        }
      } else if (wsMessage.type === "complete") {
        // Finalize assistant message
        // Use refs to get the latest values (avoiding stale closure issues)
        const finalMessage = currentMessageRef.current;
        const finalChart = pendingChartRef.current;
        const finalTable = pendingTableRef.current;

        console.log("=== COMPLETE MESSAGE RECEIVED ===");
        console.log("finalMessage length:", finalMessage?.length);
        console.log("finalChart:", finalChart);
        console.log("finalChart exists:", !!finalChart);
        console.log("finalTable rows:", finalTable?.length);

        if (finalMessage || finalChart || finalTable) {
          setMessages((prev) => {
            const newMessage = {
              type: "assistant" as const,
              content: finalMessage || "Query completed.",
              chartData: finalChart || undefined,
              tableData: finalTable || undefined,
            };
            console.log(
              "Adding new message with chartData:",
              !!newMessage.chartData
            );
            console.log("New message:", JSON.stringify(newMessage, null, 2));

            const next = [...prev, newMessage];
            // Persist conversation after state update completes
            // Use the ref to get the latest conversationId (avoids closure issues)
            const convId = conversationIdRef.current;
            setTimeout(() => {
              onPersistConversation(next, convId, true); // Use ref value to avoid race condition
            }, 0);
            return next;
          });
        }
        // Clear both state and refs immediately (avoid stale data on next message)
        currentMessageRef.current = "";
        pendingChartRef.current = null;
        pendingTableRef.current = null;
        setCurrentAssistantMessage("");
        setPendingChartData(null);
        setPendingTableData(null);
        setIsStreaming(false);
        setToolCalls([]);
      } else if (wsMessage.type === "error") {
        toast({
          title: "Error",
          description: wsMessage.content || "An error occurred",
          variant: "destructive",
        });
        setIsStreaming(false);
      }
    },
    onError: (error) => {
      // Error logging is now handled inside useWebSocket hook
      // Only show toast notification (useWebSocket will prevent duplicate calls)
      toast({
        title: "Connection Error",
        description:
          "Failed to connect to backend. Please check if the server is running.",
        variant: "destructive",
      });
      setIsStreaming(false);
    },
    autoConnect: true,
  });

  const handleSubmit = async () => {
    // Early return with console log for debugging
    if (!input.trim()) {
      console.log("[handleSubmit] Input is empty");
      return;
    }
    if (!isConnected) {
      console.log(
        "[handleSubmit] WebSocket not connected. isConnected:",
        isConnected
      );
      toast({
        title: "Not Connected",
        description: "Please wait for the connection to be established.",
        variant: "destructive",
      });
      return;
    }
    if (isStreaming) {
      console.log("[handleSubmit] Already streaming");
      return;
    }

    const userMessage = input.trim();

    // Generate or use existing conversationId BEFORE any async operations
    // This prevents race conditions where multiple conversations get created
    const currentConvId =
      conversationId ||
      (typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `${Date.now()}`);

    // Update ref immediately to prevent race condition with WebSocket complete handler
    if (!conversationId) {
      conversationIdRef.current = currentConvId;
    }

    // Add user message
    const userMsg: Message = { type: "user" as const, content: userMessage };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);

    // Persist with the guaranteed conversationId
    // Use async IIFE to avoid blocking
    (async () => {
      await onPersistConversation(updatedMessages, currentConvId, false);
    })();

    // Reset state for new response
    setCurrentAssistantMessage("");
    setPendingChartData(null);
    setPendingTableData(null);
    setToolCalls([]);
    setIsStreaming(true);

    // Send message via WebSocket with database URL and conversationId
    // This ensures conversation continuity by using the same thread_id
    const sent = sendMessage(
      userMessage,
      databaseUrl || undefined,
      currentConvId || undefined
    );

    if (!sent) {
      toast({
        title: "Error",
        description: "Failed to send message. Please check your connection.",
        variant: "destructive",
      });
      setIsStreaming(false);
    }

    setInput("");
  };

  const handleSampleQueryClick = async (query: string) => {
    if (!isConnected) {
      toast({
        title: "Not Connected",
        description: "Please wait for the connection to be established.",
        variant: "destructive",
      });
      return;
    }
    if (isStreaming) {
      return;
    }

    // Generate or use existing conversationId
    const currentConvId =
      conversationId ||
      (typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `${Date.now()}`);

    // Update ref immediately to prevent race condition
    if (!conversationId) {
      conversationIdRef.current = currentConvId;
    }

    // Add user message and persist
    setMessages((prev) => {
      const next = [...prev, { type: "user" as const, content: query }];
      setTimeout(() => {
        onPersistConversation(next, currentConvId, false);
      }, 0);
      return next;
    });

    // Reset state for new response
    setCurrentAssistantMessage("");
    setPendingChartData(null);
    setPendingTableData(null);
    setToolCalls([]);
    setIsStreaming(true);

    // Send message via WebSocket with the guaranteed conversationId
    const sent = sendMessage(
      query,
      databaseUrl || undefined,
      currentConvId || undefined
    );

    if (!sent) {
      toast({
        title: "Error",
        description: "Failed to send message. Please check your connection.",
        variant: "destructive",
      });
      setIsStreaming(false);
    }
  };

  const executeQuery = async (query: string) => {
    if (!databaseUrl) {
      toast({
        title: "Error",
        description: "Please configure a database connection first",
        variant: "destructive",
      });
      return;
    }
    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.executeQuery}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query,
            database_url: databaseUrl,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        const rows = data.rows || data.result || [];
        setMessages((prev) => {
          const next = [
            ...prev,
            {
              type: "assistant" as const,
              content: "Query results:",
              tableData: rows,
            },
          ];
          void onPersistConversation(next);
          return next;
        });
      } else {
        throw new Error("Failed to execute query");
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to execute query",
        variant: "destructive",
      });
    }
  };

  return {
    messages,
    setMessages,
    input,
    setInput,
    isStreaming,
    currentAssistantMessage,
    toolCalls,
    isConnected,
    isConnecting,
    handleSubmit,
    handleSampleQueryClick,
    executeQuery,
  };
}
