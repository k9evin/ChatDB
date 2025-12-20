'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';
import type { Message } from '@/hooks/useConversation';
import { ChartVisualization } from './chart-visualization';
import { DataTable } from './data-table';
import { MarkdownContent } from './markdown-content';
import { VegaLiteVisualization } from './vega-lite-visualization';

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

interface MessageItemProps {
  message: Message;
  dbType?: string;
}

export function MessageItem({ message, dbType }: MessageItemProps) {
  const isUser = message.type === 'user';

  return (
    <div className={`flex gap-4 w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex gap-3 max-w-[85%] md:max-w-[75%] min-w-0 ${isUser ? 'flex-row-reverse' : ''}`}>
        <Avatar className="w-10 h-10 mt-1 border border-border/50 shadow-sm shrink-0">
          <AvatarImage
            src={isUser ? '/user-avatar.png' : '/bot-avatar.png'}
            alt={isUser ? 'User' : 'Bot'}
            className="object-cover"
          />
          <AvatarFallback
            className={isUser ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'}
          >
            {isUser ? 'U' : 'AI'}
          </AvatarFallback>
        </Avatar>

        <div
          className={`relative rounded-2xl px-5 py-3.5 shadow-sm text-sm leading-relaxed min-w-0 max-w-full overflow-hidden
                        ${isUser
              ? 'bg-primary text-primary-foreground rounded-tr-none'
              : 'bg-card border border-border/50 text-card-foreground rounded-tl-none'
            }`}
        >
          {/* Content */}
          <div className={isUser ? 'text-primary-foreground' : 'text-foreground'}>
            {typeof message.content === 'string' ? (
              <MarkdownContent content={message.content} />
            ) : (
              message.content
            )}
          </div>

          {/* Display chart if available */}
          {message.chartData && (
            <div className="mt-4 pt-4 border-t border-border/20 w-full min-w-0">
              {message.chartData.vega_lite_spec ? (
                <div className="-mx-5 px-5 min-w-0">
                  <VegaLiteVisualization spec={message.chartData.vega_lite_spec} />
                </div>
              ) : (
                <div className="-mx-5 px-5 min-w-0">
                  <ChartVisualization
                    chartType={message.chartData.chart_type}
                    data={message.chartData.data}
                    config={message.chartData.config}
                  />
                </div>
              )}
            </div>
          )}

          {/* Display table data if available */}
          {message.tableData && message.tableData.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border/20 w-full min-w-0">
              <h4 className="text-xs font-semibold mb-2 opacity-70 uppercase tracking-wider">
                Query Results
              </h4>
              <div className="overflow-x-auto -mx-5 px-5">
                <DataTable data={message.tableData} dbType={dbType || ''} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
