'use client';

import { useEffect, useState } from 'react';
import { useToast } from '@/components/ui/use-toast';
import { useDatabase } from '@/contexts/database-context';

interface DatabaseConnection {
  database_url: string;
  name?: string;
  type: 'sqlite' | 'postgresql' | 'mysql' | 'demo';
}

// Demo database connection - matches backend default
const demoConnection: DatabaseConnection = {
  database_url: 'sqlite:///./demo_database.db',
  name: 'Demo Database',
  type: 'demo',
};

export function useDatabaseConnection() {
  const { setDatabaseUrl, setDbType, setDatabaseName } = useDatabase();
  const { toast } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const [connection, setConnection] = useState<DatabaseConnection>({
    database_url: '',
    type: 'demo',
  });
  const [currentConnection, setCurrentConnection] = useState<DatabaseConnection | null>(null);

  const handleConnect = async () => {
    if (!connection.database_url && connection.type !== 'demo') {
      toast({
        title: 'Error',
        description: 'Please enter a database URL',
        variant: 'destructive',
      });
      return;
    }

    const url = connection.type === 'demo' ? demoConnection.database_url : connection.database_url;

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

  return {
    isOpen,
    setIsOpen,
    connection,
    setConnection,
    currentConnection,
    setCurrentConnection,
    handleConnect,
    handleUseDemo,
  };
}
