'use client';

import { useEffect, useState } from 'react';
import { DotPattern } from '@/components/ui/dot-pattern';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/components/ui/use-toast';
import { useDatabase } from '@/contexts/database-context';
import { useChat } from '@/hooks/useChat';
import { type Message, useConversation } from '@/hooks/useConversation';
import { ChatInput } from './chat/chat-input';
import { ConversationSidebar } from './chat/conversation-sidebar';
import { MessageList } from './chat/message-list';

export function ChatLayout() {
  const { dbType, setDatabaseUrl } = useDatabase();
  const { toast } = useToast();
  const [messages, setLocalMessages] = useState<Message[]>([]);

  const {
    conversationId,
    conversations,
    isLoadingConversations,
    persistConversation,
    handleSelectConversation,
    handleDeleteConversation,
    handleNewConversation,
    handleRenameConversation,
  } = useConversation();

  const {
    messages: chatMessages,
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
  } = useChat({ onPersistConversation: persistConversation, conversationId });

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

  // Handle conversation selection and load messages
  const handleSelectConversationWithMessages = async (id: string) => {
    const loadedMessages = await handleSelectConversation(id);
    setMessages(loadedMessages);
  };

  // Handle new conversation
  const handleNewConversationWithReset = () => {
    handleNewConversation();
    setMessages([]);
  };

  // Update messages when they change in chat hook
  useEffect(() => {
    setLocalMessages(chatMessages);
  }, [chatMessages]);

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

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden relative">
      <ConversationSidebar
        conversations={conversations}
        isLoadingConversations={isLoadingConversations}
        conversationId={conversationId}
        onNewConversation={handleNewConversationWithReset}
        onSelectConversation={handleSelectConversationWithMessages}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={handleRenameConversation}
      />

      {/* Right Panel */}
      <div className="flex-1 flex flex-col relative min-w-0 bg-background text-foreground">
        <DotPattern
          width={20}
          height={20}
          cx={1}
          cy={1}
          cr={1}
          className="absolute inset-0 h-full w-full fill-neutral-200/50 dark:fill-neutral-800/50 [mask-image:radial-gradient(white,transparent_85%)]"
        />

        {/* Messages Area */}
        <div className="flex-1 overflow-hidden flex flex-col relative">
          <MessageList
            messages={messages}
            isStreaming={isStreaming}
            currentAssistantMessage={currentAssistantMessage}
            toolCalls={toolCalls}
            dbType={dbType}
            onSampleQueryClick={handleSampleQueryClick}
          />
        </div>

        {/* Input Area */}
        <div className="p-6 z-20 w-full max-w-[900px] mx-auto">
          <ChatInput
            input={input}
            setInput={setInput}
            onSubmit={handleSubmit}
            isConnected={isConnected}
            isStreaming={isStreaming}
          />
          {/* Connection Status */}
          {(!isConnected || isConnecting) && (
            <div
              className="text-xs text-muted-foreground text-center mt-2"
              role="status"
              aria-live="polite"
            >
              {isConnecting ? 'Connecting to backend...' : 'Disconnected from backend'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
