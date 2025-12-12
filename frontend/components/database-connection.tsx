'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle, Settings, Database } from 'lucide-react';
import config from '@/config';
import { useDatabase } from '@/contexts/database-context';

interface DatabaseConnection {
  database_url: string;
  name?: string;
  type: 'sqlite' | 'postgresql' | 'mysql' | 'demo';
}

// Demo database connection - matches backend default
// Moved outside component to prevent recreation on every render
const demoConnection: DatabaseConnection = {
  database_url: 'sqlite:///./demo_database.db',
  name: 'Demo Database',
  type: 'demo',
};

export function DatabaseConnection() {
  const [isOpen, setIsOpen] = useState(false);
  const [connection, setConnection] = useState<DatabaseConnection>({
    database_url: '',
    type: 'demo',
  });
  const [isTesting, setIsTesting] = useState(false);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [currentConnection, setCurrentConnection] = useState<DatabaseConnection | null>(null);
  const { toast } = useToast();
  const { setDatabaseUrl, setDbType, setDatabaseName } = useDatabase();

  const handleTypeChange = (type: string) => {
    setConnection(prev => ({
      ...prev,
      type: type as DatabaseConnection['type'],
      database_url: type === 'demo' ? demoConnection.database_url : prev.database_url,
    }));
  };

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
      const url = connection.type === 'demo'
        ? demoConnection.database_url
        : connection.database_url;

      const response = await fetch(`${config.backendUrl}/api/database/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ database_url: url }),
      });

      const data = await response.json();

      if (response.ok && data.connected) {
        setIsConnected(true);
        toast({
          title: 'Success',
          description: 'Database connection successful!',
        });
      } else {
        setIsConnected(false);
        toast({
          title: 'Connection Failed',
          description: data.error || 'Failed to connect to database',
          variant: 'destructive',
        });
      }
    } catch (error) {
      setIsConnected(false);
      toast({
        title: 'Error',
        description: 'Failed to test connection',
        variant: 'destructive',
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleConnect = async () => {
    if (!connection.database_url && connection.type !== 'demo') {
      toast({
        title: 'Error',
        description: 'Please enter a database URL',
        variant: 'destructive',
      });
      return;
    }

    const url = connection.type === 'demo'
      ? demoConnection.database_url
      : connection.database_url;

    // Store connection in localStorage
    const connectionToStore = {
      ...connection,
      database_url: url,
      name: connection.name || (connection.type === 'demo' ? 'Demo Database' : 'Custom Database'),
    };

    localStorage.setItem('chatdb_connection', JSON.stringify(connectionToStore));
    setCurrentConnection(connectionToStore);
    setDatabaseUrl(url);
    setDbType(connection.type);
    setDatabaseName(connection.name || '');
    setIsOpen(false);

    toast({
      title: 'Connected',
      description: `Connected to ${connectionToStore.name}`,
    });
  };

  const handleUseDemo = async () => {
    setConnection(demoConnection);
    await handleConnect();
  };

  // Load saved connection on mount
  // Only run once on mount - state setters are stable and don't need to be in dependencies
  useEffect(() => {
    const saved = localStorage.getItem('chatdb_connection');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setCurrentConnection(parsed);
        setConnection(parsed);
        setDatabaseUrl(parsed.database_url || null);
        setDbType(parsed.type);
        setDatabaseName(parsed.name || '');
      } catch (e) {
        // Invalid saved connection, default to demo
        setCurrentConnection(demoConnection);
        setConnection(demoConnection);
        setDatabaseUrl(demoConnection.database_url);
        setDbType('demo');
        setDatabaseName(demoConnection.name || '');
      }
    } else {
      // Default to demo
      setCurrentConnection(demoConnection);
      setConnection(demoConnection);
      setDatabaseUrl(demoConnection.database_url);
      setDbType('demo');
      setDatabaseName(demoConnection.name || '');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array - only run once on mount

  const getConnectionString = () => {
    if (connection.type === 'demo') {
      return demoConnection.database_url;
    }
    return connection.database_url;
  };

  return (
    <div className="space-y-2">
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm" className="w-full">
            <Settings className="mr-2 h-4 w-4" />
            Database Connection
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Configure Database Connection</DialogTitle>
            <DialogDescription>
              Connect to a database or use the demo database to get started.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="db-type">Database Type</Label>
              <Select value={connection.type} onValueChange={handleTypeChange}>
                <SelectTrigger id="db-type">
                  <SelectValue placeholder="Select database type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="demo">Demo Database (SQLite)</SelectItem>
                  <SelectItem value="sqlite">SQLite</SelectItem>
                  <SelectItem value="postgresql">PostgreSQL</SelectItem>
                  <SelectItem value="mysql">MySQL</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {connection.type === 'demo' ? (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Demo Database</CardTitle>
                  <CardDescription>
                    A pre-configured sample database with customers, orders, and products tables.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Label>Connection String</Label>
                    <Input value={demoConnection.database_url} disabled />
                    <Button
                      onClick={handleUseDemo}
                      className="w-full mt-2"
                      variant="default"
                    >
                      <Database className="mr-2 h-4 w-4" />
                      Use Demo Database
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <>
                <div className="space-y-2">
                  <Label htmlFor="db-name">Connection Name (Optional)</Label>
                  <Input
                    id="db-name"
                    placeholder="My Database"
                    value={connection.name || ''}
                    onChange={(e) => setConnection(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="db-url">Database URL</Label>
                  <Input
                    id="db-url"
                    placeholder={
                      connection.type === 'sqlite'
                        ? 'sqlite:///./path/to/database.db'
                        : connection.type === 'postgresql'
                          ? 'postgresql://user:password@localhost:5432/dbname'
                          : 'mysql://user:password@localhost:3306/dbname'
                    }
                    value={connection.database_url}
                    onChange={(e) => setConnection(prev => ({ ...prev, database_url: e.target.value }))}
                  />
                  <p className="text-xs text-muted-foreground">
                    {connection.type === 'sqlite' && 'Example: sqlite:///./database.db'}
                    {connection.type === 'postgresql' && 'Example: postgresql://user:pass@localhost:5432/mydb'}
                    {connection.type === 'mysql' && 'Example: mysql://user:pass@localhost:3306/mydb'}
                  </p>
                </div>
              </>
            )}

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={handleTestConnection}
                disabled={isTesting || connection.type === 'demo'}
                className="flex-1"
              >
                {isTesting ? 'Testing...' : 'Test Connection'}
              </Button>
              <Button
                onClick={handleConnect}
                disabled={isTesting}
                className="flex-1"
              >
                Connect
              </Button>
            </div>

            {isConnected !== null && (
              <div className="flex items-center gap-2 text-sm">
                {isConnected ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span className="text-green-500">Connection successful</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-4 w-4 text-red-500" />
                    <span className="text-red-500">Connection failed</span>
                  </>
                )}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {currentConnection && (
        <div className="text-xs text-muted-foreground flex items-center gap-2">
          <Database className="h-3 w-3" />
          <span className="truncate">
            {currentConnection.name || 'Connected'}
          </span>
          <Badge variant="outline" className="text-xs">
            {currentConnection.type}
          </Badge>
        </div>
      )}
    </div>
  );
}

