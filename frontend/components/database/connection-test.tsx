'use client';

import { CheckCircle2, XCircle } from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import config from '@/config';

interface DatabaseConnection {
  database_url: string;
  name?: string;
  type: 'sqlite' | 'postgresql' | 'mysql' | 'demo';
}

interface ConnectionTestProps {
  connection: DatabaseConnection;
  onTestResult: (isConnected: boolean) => void;
}

export function ConnectionTest({ connection, onTestResult }: ConnectionTestProps) {
  const [isTesting, setIsTesting] = useState(false);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const { toast } = useToast();

  const handleTestConnection = async () => {
    if (!connection.database_url && connection.type !== 'demo') {
      toast({
        title: 'Error',
        description: 'Please enter a database URL',
        variant: 'destructive',
      });
      return;
    }

    setIsTesting(true);
    setIsConnected(null);

    try {
      const url =
        connection.type === 'demo' ? 'sqlite:///./demo_database.db' : connection.database_url;

      const response = await fetch(`${config.backendUrl}/api/database/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ database_url: url }),
      });

      const data = await response.json();

      if (response.ok && data.connected) {
        setIsConnected(true);
        onTestResult(true);
        toast({
          title: 'Success',
          description: 'Database connection successful!',
        });
      } else {
        setIsConnected(false);
        onTestResult(false);
        toast({
          title: 'Connection Failed',
          description: data.error || 'Failed to connect to database',
          variant: 'destructive',
        });
      }
    } catch (error) {
      setIsConnected(false);
      onTestResult(false);
      toast({
        title: 'Error',
        description: 'Failed to test connection',
        variant: 'destructive',
      });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={handleTestConnection}
          disabled={isTesting || connection.type === 'demo'}
          className="flex-1"
        >
          {isTesting ? 'Testing...' : 'Test Connection'}
        </Button>
      </div>

      {isConnected !== null && (
        <div className="flex items-center gap-2 text-sm">
          {isConnected ? (
            <>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <span className="text-green-500">Connection successful</span>
              <Badge variant="outline" className="text-xs">
                Connected
              </Badge>
            </>
          ) : (
            <>
              <XCircle className="h-4 w-4 text-red-500" />
              <span className="text-red-500">Connection failed</span>
              <Badge variant="destructive" className="text-xs">
                Failed
              </Badge>
            </>
          )}
        </div>
      )}
    </div>
  );
}
