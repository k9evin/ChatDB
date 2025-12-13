'use client';

import { useEffect, useRef } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { Message } from '@/hooks/useConversation';
import { MessageItem } from './message-item';
import { SampleQueriesEmptyState } from './sample-queries-empty-state';
import { StreamingMessage } from './streaming-message';

interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
  currentAssistantMessage: string;
  toolCalls: string[];
  dbType?: string;
  onSampleQueryClick: (query: string) => void;
}

export function MessageList({
  messages,
  isStreaming,
  currentAssistantMessage,
  toolCalls,
  dbType,
  onSampleQueryClick,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<React.ElementRef<typeof ScrollArea>>(null);

  // Auto-scroll to bottom when messages change or streaming updates
  const scrollToBottom = () => {
    // Use requestAnimationFrame to ensure DOM has updated
    requestAnimationFrame(() => {
      if (scrollAreaRef.current) {
        // Access the viewport element from Radix UI ScrollArea
        const viewport = scrollAreaRef.current.querySelector(
          '[data-radix-scroll-area-viewport]'
        ) as HTMLElement;
        if (viewport) {
          viewport.scrollTo({ top: viewport.scrollHeight, behavior: 'smooth' });
        }
      }
      // Fallback: use scrollIntoView on the end marker
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  };

  // Scroll when messages change (user messages or completed assistant messages)
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Scroll when streaming starts
  useEffect(() => {
    if (isStreaming) {
      scrollToBottom();
    }
  }, [isStreaming]);

  // Throttled scroll during streaming updates
  useEffect(() => {
    if (isStreaming && currentAssistantMessage) {
      // Use a throttled scroll for streaming updates to avoid too frequent scrolling
      const timeoutId = setTimeout(() => {
        scrollToBottom();
      }, 300); // Scroll every 300ms during streaming
      return () => clearTimeout(timeoutId);
    }
  }, [isStreaming, currentAssistantMessage]);

  return (
    <ScrollArea ref={scrollAreaRef} className="flex-1 mb-4 pr-4">
      <div className="max-w-4xl mx-auto w-full px-4">
        {/* Show empty state when no messages and not streaming */}
        {messages.length === 0 && !isStreaming ? (
          <SampleQueriesEmptyState onQueryClick={onSampleQueryClick} />
        ) : (
          <div className="space-y-6 py-6">
            {messages.map((message, index) => (
              <MessageItem key={index} message={message} dbType={dbType} />
            ))}

            {/* Streaming message */}
            {isStreaming && (
              <StreamingMessage
                currentAssistantMessage={currentAssistantMessage}
                toolCalls={toolCalls}
              />
            )}
            {/* Invisible element to scroll to */}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
