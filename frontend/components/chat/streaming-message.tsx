'use client';

import { Loader2 } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';
import { MarkdownContent } from './markdown-content';

interface StreamingMessageProps {
  currentAssistantMessage: string;
  toolCalls: string[];
}

export function StreamingMessage({ currentAssistantMessage, toolCalls }: StreamingMessageProps) {
  return (
    <div className="flex gap-3 justify-start">
      <div className="flex gap-3 max-w-[80%]">
        <Avatar className="w-10 h-10 mt-1 border border-border/50 shadow-sm shrink-0">
          <AvatarImage src="/bot-avatar.png" alt="Bot" className="object-cover" />
          <AvatarFallback className="bg-muted text-muted-foreground">AI</AvatarFallback>
        </Avatar>
        <Card>
          <CardContent className="p-4 text-sm leading-relaxed">
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
  );
}
