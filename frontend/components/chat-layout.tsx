'use client';

import { useState } from 'react';
import { FileUpload } from './file-upload';
import { DatabaseExplorer } from './database-explorer';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import config from '@/config';
import { useDatabase } from '@/contexts/database-context';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { DataTable } from './chat/data-table';
import { SampleQueriesList } from './chat/sample-queries-list';
import { GeneratedQuery } from './chat/generated-query';

interface Message {
  type: 'user' | 'assistant';
  content: string | React.ReactNode;
}

export function ChatLayout() {
  const { dbType, selectedTable, databaseName } = useDatabase();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const { toast } = useToast();

  const handleSubmit = async () => {
    if (!input.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { type: 'user', content: input }]);

    // Check for special commands
    const normalizedInput = input.toLowerCase().trim();
    
    try {
      if (normalizedInput === 'generate sample data') {
        await handleGenerateSampleData(false);
      } 
      else if (normalizedInput === 'generate sample queries') {
        await handleGenerateSampleQueries(false);
      } 
      else {
        // Handle as natural language query
        if (!selectedTable || !databaseName) {
          toast({
            title: 'Error',
            description: 'Please select a database and table first',
            variant: 'destructive',
          });
          return;
        }

        const response = await fetch(
          `${config.backendUrl}${config.api.naturalLanguageQuery}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              query: input,
              db_type: dbType,
              table_name: selectedTable,
              database_name: databaseName,
            }),
          }
        );

        if (response.ok) {
          const data = await response.json();
          if (data.generated_query) {
            setMessages(prev => [...prev, {
              type: 'assistant',
              content: <GeneratedQuery query={data.generated_query} onExecute={executeQuery} />
            }]);
          } else {
            setMessages(prev => [...prev, {
              type: 'assistant',
              content: data.message || 'I could not generate a query for your request.'
            }]);
          }
        } else {
          const errorData = await response.json();
          toast({
            title: 'Error',
            description: errorData.detail || 'Failed to process natural language query',
            variant: 'destructive',
          });
        }
      }
    } catch (error) {
      console.error('Error processing input:', error);
      toast({
        title: 'Error',
        description: 'An unexpected error occurred',
        variant: 'destructive',
      });
    } finally {
      setInput('');
    }
  };

  const handleGenerateSampleData = async (quickAction: boolean = true) => {
    if (!selectedTable || !databaseName) {
      toast({
        title: 'Error',
        description: 'Please select a database and table first',
        variant: 'destructive',
      });
      return;
    }
    if (quickAction) {
      const userMessage = "Generate sample data for the current table";
      setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    }

    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.sampleData}?db_type=${dbType}&table_name=${selectedTable}&database_name=${databaseName}`
      );

      if (response.ok) {
        const data = await response.json();
        const sampleData = dbType === 'mysql' ? data : data.result || data;

        setMessages(prev => [...prev, {
          type: 'assistant',
          content: (
            <div>
              <p className="mb-4">Here's the sample data from your table:</p>
              <DataTable data={sampleData} dbType={dbType} />
            </div>
          )
        }]);
      } else {
        throw new Error('Failed to fetch sample data');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch sample data',
        variant: 'destructive',
      });
    }
  };

  const handleGenerateSampleQueries = async (quickAction: boolean = true) => {
    if (!selectedTable || !databaseName) {
      toast({
        title: 'Error',
        description: 'Please select a database and table first',
        variant: 'destructive',
      });
      return;
    }
    if (quickAction) {
      const userMessage = "Generate sample queries for the current table";
      setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    }

    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.sampleQueries}?db_type=${dbType}&table_name=${selectedTable}&database_name=${databaseName}`
      );

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: (
            <div>
              <p className="mb-4">Here are some sample queries you can try:</p>
              <SampleQueriesList 
                queries={data.sample_queries} 
                dbType={dbType} 
                onExecute={executeQuery} 
              />
            </div>
          )
        }]);
      } else {
        throw new Error('Failed to fetch sample queries');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch sample queries',
        variant: 'destructive',
      });
    }
  };

  const executeQuery = async (query: string) => {
    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.executeQuery}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query,
            db_type: dbType,
            table_name: selectedTable,
            database_name: databaseName,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: (
            <div>
              <p className="mb-4">Query results:</p>
              <DataTable data={data.result} dbType={dbType} />
            </div>
          )
        }]);
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
      {/* Left Panel */}
      <div className="w-1/5 flex flex-col gap-4">
        <div className="flex-none">
          <p className="text-3xl font-bold">ChatDB</p>
          <span className="text-base text-muted-foreground -mt-4">
            Chat with your data
          </span>
        </div>
        <div className="flex flex-col flex-1 min-h-0 gap-4">
          <FileUpload className="flex-none" />
          <DatabaseExplorer className="flex-1 overflow-auto" />
        </div>
      </div>

      {/* Divider */}
      <Separator orientation="vertical" className="h-full" />

      {/* Right Panel */}
      <div className="flex-1 flex flex-col">
        {/* Messages Area */}
        <ScrollArea className="flex-1 mb-4 pr-4">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`flex gap-3 max-w-[80%] ${
                    message.type === 'user' ? 'flex-row-reverse' : ''
                  }`}
                >
                  <Avatar className="w-8 h-8">
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
                    className={`${
                      message.type === 'assistant'
                        ? ''
                        : 'bg-muted'
                    }`}
                  >
                    <CardContent className="p-4">
                      {typeof message.content === 'string' ? (
                        <p>{message.content}</p>
                      ) : (
                        message.content
                      )}
                    </CardContent>
                  </Card>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Quick Actions */}
        <div className="flex gap-2 mb-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleGenerateSampleData(true)}
          >
            Generate Sample Data
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleGenerateSampleQueries(true)}
          >
            Generate Sample Queries
          </Button>
        </div>

        {/* Input Area */}
        <div className="flex gap-2 justify-center items-center">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message ChatDB..."
            className="flex-1"
          />
          <Button onClick={handleSubmit}>Submit</Button>
        </div>
      </div>
    </div>
  );
} 