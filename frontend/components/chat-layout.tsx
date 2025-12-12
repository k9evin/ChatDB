'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import config from '@/config';
import { useDatabase } from '@/contexts/database-context';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { DataTable } from './chat/data-table';
import { ChartVisualization } from './chat/chart-visualization';
import { VegaLiteVisualization } from './chat/vega-lite-visualization';
import { MarkdownContent } from './chat/markdown-content';
import { ConversationMeta, StoredMessage, listConversations, loadConversation, saveConversation, deleteConversation } from '@/lib/conversation-store';
import { Loader2, Sparkles, ArrowUp, Plus } from "lucide-react";
import { useWebSocket } from '@/hooks/useWebSocket';
import { DatabaseConnection } from './database-connection';
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader } from '@/components/ui/sidebar';
import { SampleQueriesEmptyState } from './chat/sample-queries-empty-state';

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

interface Message {
  type: 'user' | 'assistant';
  content: string | React.ReactNode;
  chartData?: ChartData;
  tableData?: any[];
}

export function ChatLayout() {
  const { dbType, databaseName, databaseUrl, setDatabaseUrl } = useDatabase();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentAssistantMessage, setCurrentAssistantMessage] = useState('');
  const [toolCalls, setToolCalls] = useState<string[]>([]);
  const [pendingChartData, setPendingChartData] = useState<ChartData | null>(null);
  const [pendingTableData, setPendingTableData] = useState<any[] | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationMeta[]>([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const { toast } = useToast();

  // Use refs to store latest values for use in callbacks
  const currentMessageRef = useRef('');
  const pendingChartRef = useRef<ChartData | null>(null);
  const pendingTableRef = useRef<any[] | null>(null);
  const conversationIdRef = useRef<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<React.ElementRef<typeof ScrollArea>>(null);

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

  // Auto-scroll to bottom when messages change or streaming updates
  const scrollToBottom = useCallback(() => {
    // Use requestAnimationFrame to ensure DOM has updated
    requestAnimationFrame(() => {
      if (scrollAreaRef.current) {
        // Access the viewport element from Radix UI ScrollArea
        const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]') as HTMLElement;
        if (viewport) {
          viewport.scrollTo({ top: viewport.scrollHeight, behavior: 'smooth' });
        }
      }
      // Fallback: use scrollIntoView on the end marker
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }, []);

  // Scroll when messages change (user messages or completed assistant messages)
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Scroll when streaming starts
  useEffect(() => {
    if (isStreaming) {
      scrollToBottom();
    }
  }, [isStreaming, scrollToBottom]);

  // Throttled scroll during streaming updates
  useEffect(() => {
    if (isStreaming && currentAssistantMessage) {
      // Use a throttled scroll for streaming updates to avoid too frequent scrolling
      const timeoutId = setTimeout(() => {
        scrollToBottom();
      }, 300); // Scroll every 300ms during streaming
      return () => clearTimeout(timeoutId);
    }
  }, [isStreaming, currentAssistantMessage, scrollToBottom]);

  const serializeMessage = useCallback((msg: Message): StoredMessage => ({
    type: msg.type,
    content: typeof msg.content === 'string' ? msg.content : '',
    chartData: msg.chartData,
    tableData: msg.tableData,
  }), []);

  const refreshConversations = useCallback(async (preferId?: string | null, skipMessageUpdate = false) => {
    setIsLoadingConversations(true);
    const list = await listConversations();
    setConversations(list);
    const targetId = preferId || list[0]?.id || null;
    if (targetId) {
      const convo = await loadConversation(targetId);
      if (convo) {
        setConversationId(targetId);
        // Only update messages if not streaming (to prevent losing in-progress messages)
        if (!skipMessageUpdate) {
          setMessages(convo.messages as Message[]);
        }
        setDatabaseUrl(convo.databaseUrl || null);
      }
    }
    setIsLoadingConversations(false);
  }, [setDatabaseUrl]);

  useEffect(() => {
    refreshConversations();
  }, [refreshConversations]);

  const persistConversation = useCallback(async (updatedMessages: Message[], id?: string | null, skipRefresh = false) => {
    // Use provided id, or existing conversationId, or create new one
    // Only create new conversation if id is explicitly null/undefined AND conversationId is also null
    const convId = id !== undefined && id !== null
      ? id
      : (conversationId || (typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}`));

    // Load existing conversation to preserve createdAt if it exists
    const existing = convId ? await loadConversation(convId) : null;
    const createdAt = existing?.createdAt || Date.now();

    const firstUser = updatedMessages.find((m) => m.type === 'user');
    const title = firstUser && typeof firstUser.content === 'string'
      ? firstUser.content.slice(0, 60)
      : (existing?.title || 'Conversation');
    const now = Date.now();
    const record = {
      id: convId,
      title,
      createdAt,
      updatedAt: now,
      databaseUrl,
      messages: updatedMessages.map(serializeMessage),
    };
    await saveConversation(record);
    setConversationId(convId);
    // Only refresh conversations list if not streaming and not explicitly skipped
    // This prevents overwriting in-progress streaming messages
    if (!skipRefresh && !isStreaming) {
      await refreshConversations(convId, true); // Skip message update to preserve current state
    }
  }, [conversationId, databaseUrl, refreshConversations, serializeMessage, isStreaming]);

  const handleSelectConversation = useCallback(async (id: string) => {
    const convo = await loadConversation(id);
    if (convo) {
      setConversationId(id);
      setMessages(convo.messages as Message[]);
      setDatabaseUrl(convo.databaseUrl || null);
    }
  }, [setDatabaseUrl]);

  const handleDeleteConversation = useCallback(async (id: string) => {
    await deleteConversation(id);
    if (conversationId === id) {
      setConversationId(null);
      setMessages([]);
    }
    await refreshConversations();
  }, [conversationId, refreshConversations]);

  const handleNewConversation = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setCurrentAssistantMessage('');
    setPendingChartData(null);
    setPendingTableData(null);
  }, []);

  const handleRenameConversation = useCallback(async (id: string) => {
    const current = conversations.find((c) => c.id === id);
    const nextTitle = window.prompt('Conversation name', current?.title || 'Conversation');
    if (!nextTitle) return;
    const convo = await loadConversation(id);
    if (convo) {
      const updated = { ...convo, title: nextTitle, updatedAt: Date.now() };
      await saveConversation(updated);
      await refreshConversations(id);
    }
  }, [conversations, refreshConversations]);

  // Load database URL from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('chatdb_connection');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setDatabaseUrl(parsed.database_url || null);
      } catch (e) {
        // Invalid saved connection
      }
    }
  }, [setDatabaseUrl]);

  // WebSocket connection
  const wsUrl = config.backendUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws/chat';

  const { isConnected, sendMessage, isConnecting } = useWebSocket({
    url: wsUrl,
    onMessage: (wsMessage) => {
      if (wsMessage.type === 'token') {
        // Append token to current assistant message
        setCurrentAssistantMessage(prev => prev + (wsMessage.content || ''));
      } else if (wsMessage.type === 'tool_start') {
        // Track tool usage
        const toolName = wsMessage.tool || 'unknown';
        setToolCalls(prev => [...prev, toolName]);
      } else if (wsMessage.type === 'tool_result') {
        // Tool execution completed
        console.log('[WebSocket] Tool result:', wsMessage.tool, wsMessage.output);

        // Parse tool output - backend sends ToolMessage with content as JSON string
        let output = wsMessage.output || {};

        // If output has a content field with JSON string, parse it
        if (output.content && typeof output.content === 'string') {
          try {
            output = JSON.parse(output.content);
            console.log('[WebSocket] Parsed output:', output);
          } catch (e) {
            console.warn('[WebSocket] Failed to parse output.content as JSON:', e);
          }
        }

        // Check if this is a chart suggestion or execution result
        if (wsMessage.tool === 'suggest_chart_type') {
          console.log('[WebSocket] suggest_chart_type output:', output);
          if (output.should_visualize && output.chart_type && output.chart_type !== 'table') {
            // Store chart data for when message completes
            const chartData = {
              chart_type: output.chart_type,
              data: output.data || [],
              config: output.chart_config || {}
            };
            console.log('[WebSocket] Setting pending chart data from suggest_chart_type:', chartData);
            // IMPORTANT: update ref immediately to avoid race with `complete`
            pendingChartRef.current = chartData;
            setPendingChartData(chartData);
          }
        } else if (wsMessage.tool === 'prepare_chart_data') {
          console.log('[WebSocket] prepare_chart_data output:', output);
          if (output.chart_type && output.chart_type !== 'table') {
            // Store prepared chart data (this is the final chart data ready for visualization)
            const chartData = {
              chart_type: output.chart_type,
              data: output.data || [],
              config: output.config || {},
              vega_lite_spec: output.vega_lite_spec || undefined,
            };
            console.log('[WebSocket] Setting pending chart data from prepare_chart_data:', chartData);
            // IMPORTANT: update ref immediately to avoid race with `complete`
            pendingChartRef.current = chartData;
            setPendingChartData(chartData);
          }
        } else if (wsMessage.tool === 'execute_sql_query' && output?.rows) {
          // Store table data (rows might be in output directly or in output.rows)
          const rows = output.rows || [];
          pendingTableRef.current = rows;
          setPendingTableData(rows);
        }
      } else if (wsMessage.type === 'complete') {
        // Finalize assistant message
        // Use refs to get the latest values (avoiding stale closure issues)
        const finalMessage = currentMessageRef.current;
        const finalChart = pendingChartRef.current;
        const finalTable = pendingTableRef.current;

        console.log('=== COMPLETE MESSAGE RECEIVED ===');
        console.log('finalMessage length:', finalMessage?.length);
        console.log('finalChart:', finalChart);
        console.log('finalChart exists:', !!finalChart);
        console.log('finalTable rows:', finalTable?.length);

        if (finalMessage || finalChart || finalTable) {
          setMessages(prev => {
            const newMessage = {
              type: 'assistant' as const,
              content: finalMessage || 'Query completed.',
              chartData: finalChart || undefined,
              tableData: finalTable || undefined
            };
            console.log('Adding new message with chartData:', !!newMessage.chartData);
            console.log('New message:', JSON.stringify(newMessage, null, 2));

            const next = [...prev, newMessage];
            // Persist conversation after state update completes
            // Use the ref to get the latest conversationId (avoids closure issues)
            const convId = conversationIdRef.current;
            setTimeout(() => {
              persistConversation(next, convId, true); // Use ref value to avoid race condition
            }, 0);
            return next;
          });
        }
        // Clear both state and refs immediately (avoid stale data on next message)
        currentMessageRef.current = '';
        pendingChartRef.current = null;
        pendingTableRef.current = null;
        setCurrentAssistantMessage('');
        setPendingChartData(null);
        setPendingTableData(null);
        setIsStreaming(false);
        setToolCalls([]);
      } else if (wsMessage.type === 'error') {
        toast({
          title: 'Error',
          description: wsMessage.content || 'An error occurred',
          variant: 'destructive',
        });
        setIsStreaming(false);
      }
    },
    onError: (error) => {
      // Error logging is now handled inside useWebSocket hook
      // Only show toast notification (useWebSocket will prevent duplicate calls)
      toast({
        title: 'Connection Error',
        description: 'Failed to connect to backend. Please check if the server is running.',
        variant: 'destructive',
      });
      setIsStreaming(false);
    },
    autoConnect: true,
  });

  const handleSubmit = async () => {
    // Early return with console log for debugging
    if (!input.trim()) {
      console.log('[handleSubmit] Input is empty');
      return;
    }
    if (!isConnected) {
      console.log('[handleSubmit] WebSocket not connected. isConnected:', isConnected);
      toast({
        title: 'Not Connected',
        description: 'Please wait for the connection to be established.',
        variant: 'destructive',
      });
      return;
    }
    if (isStreaming) {
      console.log('[handleSubmit] Already streaming');
      return;
    }

    const userMessage = input.trim();

    // Generate or use existing conversationId BEFORE any async operations
    // This prevents race conditions where multiple conversations get created
    const currentConvId = conversationId || (typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}`);

    // Set conversationId immediately if it was just generated
    if (!conversationId) {
      setConversationId(currentConvId);
      conversationIdRef.current = currentConvId; // Update ref immediately
    }

    // Add user message
    const userMsg: Message = { type: 'user' as const, content: userMessage };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);

    // Persist with the guaranteed conversationId
    // Use async IIFE to avoid blocking
    (async () => {
      await persistConversation(updatedMessages, currentConvId, false);
    })();

    // Reset state for new response
    setCurrentAssistantMessage('');
    setPendingChartData(null);
    setPendingTableData(null);
    setToolCalls([]);
    setIsStreaming(true);

    // Send message via WebSocket with database URL and conversationId
    // This ensures conversation continuity by using the same thread_id
    const sent = sendMessage(userMessage, databaseUrl || undefined, currentConvId || undefined);

    if (!sent) {
      toast({
        title: 'Error',
        description: 'Failed to send message. Please check your connection.',
        variant: 'destructive',
      });
      setIsStreaming(false);
    }

    setInput('');
  };

  const handleSampleQueryClick = async (query: string) => {
    if (!isConnected) {
      toast({
        title: 'Not Connected',
        description: 'Please wait for the connection to be established.',
        variant: 'destructive',
      });
      return;
    }
    if (isStreaming) {
      return;
    }

    // Add user message and persist
    setMessages(prev => {
      const next = [...prev, { type: 'user' as const, content: query }];
      setTimeout(() => {
        persistConversation(next, conversationId, false);
      }, 0);
      return next;
    });

    // Reset state for new response
    setCurrentAssistantMessage('');
    setPendingChartData(null);
    setPendingTableData(null);
    setToolCalls([]);
    setIsStreaming(true);

    // Send message via WebSocket
    const sent = sendMessage(query, databaseUrl || undefined, conversationId || undefined);

    if (!sent) {
      toast({
        title: 'Error',
        description: 'Failed to send message. Please check your connection.',
        variant: 'destructive',
      });
      setIsStreaming(false);
    }
  };

  // Listen for database connection changes
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('chatdb_connection');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setDatabaseUrl(parsed.database_url || null);
        } catch (e) {
          // Invalid saved connection
        }
      } else {
        setDatabaseUrl(null);
      }
    };

    // Listen for storage events (from other tabs)
    window.addEventListener('storage', handleStorageChange);

    // Also check periodically (for same-tab updates)
    // Increased interval to 2 seconds to reduce CPU usage
    const interval = setInterval(handleStorageChange, 2000);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [setDatabaseUrl]);



  const executeQuery = async (query: string) => {
    if (!databaseUrl) {
      toast({
        title: 'Error',
        description: 'Please configure a database connection first',
        variant: 'destructive',
      });
      return;
    }
    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.executeQuery}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query,
            database_url: databaseUrl,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        const rows = data.rows || data.result || [];
        setMessages(prev => {
          const next = [...prev, {
            type: 'assistant' as const,
            content: 'Query results:',
            tableData: rows,
          }];
          void persistConversation(next);
          return next;
        });
      } else {
        throw new Error('Failed to execute query');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to execute query',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="flex h-[calc(100vh-2rem)] gap-4 m-4">
      <Sidebar className="h-full">
        <SidebarHeader>
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold leading-tight">ChatDB</p>
              <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-primary/10 text-primary text-xs font-medium">
                <Sparkles className="h-3 w-3" />
                <span>AI Agent</span>
              </div>
            </div>
            <span className="text-sm text-muted-foreground">
              Intelligent database assistant powered by AI
            </span>
          </div>
        </SidebarHeader>

        <SidebarContent className="flex flex-col !px-0 !py-0">
          {/* New Chat Button */}
          <div className="px-4 pt-3 pb-2">
            <button
              onClick={handleNewConversation}
              className="flex items-center gap-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>New chat</span>
            </button>
          </div>

          {/* RECENTS Header */}
          <div className="px-4 mb-2">
            <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Recents
            </h3>
          </div>

          {/* Conversations List - Scrollable */}
          <div className="flex-1 overflow-y-auto px-4 pb-3 min-h-0">
            {isLoadingConversations && (
              <div className="py-4 text-xs text-muted-foreground text-center">Loading...</div>
            )}
            {!isLoadingConversations && conversations.length === 0 && (
              <div className="py-4 text-xs text-muted-foreground text-center">No conversations yet.</div>
            )}
            {!isLoadingConversations && conversations.length > 0 && (
              <div className="space-y-1">
                {conversations.map((convo) => (
                  <div
                    key={convo.id}
                    className={`group relative rounded-lg px-3 py-2.5 text-sm cursor-pointer transition-colors ${conversationId === convo.id
                      ? 'bg-muted'
                      : 'hover:bg-muted/50'
                      }`}
                    onClick={() => handleSelectConversation(convo.id)}
                  >
                    <div className="truncate pr-8">
                      {convo.title || 'Conversation'}
                    </div>
                    {/* Delete button - only show on hover */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteConversation(convo.id);
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-destructive/10 rounded text-muted-foreground hover:text-destructive"
                      aria-label="Delete conversation"
                    >
                      <svg
                        className="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </SidebarContent>

        <SidebarFooter>
          <DatabaseConnection />
        </SidebarFooter>
      </Sidebar>

      {/* Divider */}
      <Separator orientation="vertical" className="h-full" />

      {/* Right Panel */}
      <div className="flex-1 flex flex-col">
        {/* Messages Area */}
        <ScrollArea ref={scrollAreaRef} className="flex-1 mb-4 pr-4">
          {/* Show empty state when no messages and not streaming */}
          {messages.length === 0 && !isStreaming ? (
            <SampleQueriesEmptyState onQueryClick={handleSampleQueryClick} />
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                >
                  <div
                    className={`flex gap-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : ''
                      }`}
                  >
                    <Avatar className="w-12 h-12">
                      <AvatarImage
                        src={
                          message.type === 'assistant'
                            ? '/bot-avatar.png'
                            : '/user-avatar.png'
                        }
                        alt={message.type === 'assistant' ? 'Bot' : 'User'}
                      />
                      <AvatarFallback>
                        {message.type === 'assistant' ? 'B' : 'U'}
                      </AvatarFallback>
                    </Avatar>
                    <Card
                      className={`${message.type === 'assistant'
                        ? ''
                        : 'bg-muted'
                        }`}
                    >
                      <CardContent className="p-4 space-y-4">
                        {typeof message.content === 'string' ? (
                          <MarkdownContent content={message.content} />
                        ) : (
                          message.content
                        )}

                        {/* Display chart if available */}
                        {message.chartData && (
                          <div className="mt-4 border-t pt-4">
                            {(() => {
                              console.log('=== RENDERING CHART ===');
                              console.log('chartData:', message.chartData);
                              console.log('chart_type:', message.chartData.chart_type);
                              console.log('data length:', message.chartData.data?.length);
                              console.log('has vega_lite_spec:', !!message.chartData.vega_lite_spec);
                              return null;
                            })()}
                            {message.chartData.vega_lite_spec ? (
                              <VegaLiteVisualization spec={message.chartData.vega_lite_spec} />
                            ) : (
                              <ChartVisualization
                                chartType={message.chartData.chart_type}
                                data={message.chartData.data}
                                config={message.chartData.config}
                              />
                            )}
                          </div>
                        )}

                        {/* Display table data if available */}
                        {message.tableData && message.tableData.length > 0 && (
                          <div className="mt-4 border-t pt-4">
                            <h4 className="text-sm font-semibold mb-2">Query Results:</h4>
                            <DataTable data={message.tableData} dbType={dbType} />
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </div>
              ))}

              {/* Streaming message */}
              {isStreaming && (
                <div className="flex gap-3 justify-start">
                  <div className="flex gap-3 max-w-[80%]">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src="/bot-avatar.png" alt="Bot" />
                      <AvatarFallback>B</AvatarFallback>
                    </Avatar>
                    <Card>
                      <CardContent className="p-4">
                        {currentAssistantMessage ? (
                          <MarkdownContent content={currentAssistantMessage} />
                        ) : (
                          <div className="flex items-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-muted-foreground">Thinking...</span>
                          </div>
                        )}
                        {toolCalls.length > 0 && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            Using: {toolCalls.join(', ')}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}
              {/* Invisible element to scroll to */}
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>


        {/* Input Area */}
        <div className="flex justify-center items-center relative z-10">
          <div className="flex-1 max-w-4xl rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#3C3B3F] shadow-sm relative">
            {/* Textarea Section */}
            <div className="px-4 pt-4 pb-2">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                placeholder="How can I help you today?"
                className="min-h-[60px] border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 resize-none text-base placeholder:text-gray-500 dark:placeholder:text-[#B0B0B0] text-gray-900 dark:text-[#B0B0B0]"
                disabled={!isConnected || isStreaming}
                aria-label="Message input"
                id="chat-input"
              />
            </div>

            {/* Control Bar */}
            <div className="flex items-center justify-end px-4 pb-3 gap-2 relative z-10">
              <Button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleSubmit();
                }}
                disabled={!isConnected || isStreaming || !input.trim()}
                aria-label="Send message"
                id="send-button"
                type="button"
                className="h-10 w-10 p-0 rounded-lg bg-[#DC9783] dark:bg-[#9B492B] hover:bg-[#DC9783]/90 dark:hover:bg-[#9B492B]/90 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-opacity relative z-10"
                title={
                  !isConnected
                    ? 'Waiting for connection...'
                    : isStreaming
                      ? 'Processing...'
                      : !input.trim()
                        ? 'Please enter a message'
                        : 'Send message'
                }
              >
                {isStreaming ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <ArrowUp className="h-5 w-5" />
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Connection Status */}
        {(!isConnected || isConnecting) && (
          <div className="text-xs text-muted-foreground text-center mt-2" role="status" aria-live="polite">
            {isConnecting ? 'Connecting to backend...' : 'Disconnected from backend'}
          </div>
        )}
      </div>
    </div>
  );
} 