'use client';

import { Database } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

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

interface ConnectionConfigProps {
  connection: DatabaseConnection;
  onConnectionChange: (connection: DatabaseConnection) => void;
  onUseDemo: () => void;
}

export function ConnectionConfig({
  connection,
  onConnectionChange,
  onUseDemo,
}: ConnectionConfigProps) {
  const handleTypeChange = (type: string) => {
    onConnectionChange({
      ...connection,
      type: type as DatabaseConnection['type'],
      database_url: type === 'demo' ? demoConnection.database_url : connection.database_url,
    });
  };

  const handleNameChange = (name: string) => {
    onConnectionChange({ ...connection, name });
  };

  const handleUrlChange = (database_url: string) => {
    onConnectionChange({ ...connection, database_url });
  };

  return (
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
              <Button onClick={onUseDemo} className="w-full mt-2" variant="default">
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
              onChange={(e) => handleNameChange(e.target.value)}
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
              onChange={(e) => handleUrlChange(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              {connection.type === 'sqlite' && 'Example: sqlite:///./database.db'}
              {connection.type === 'postgresql' &&
                'Example: postgresql://user:pass@localhost:5432/mydb'}
              {connection.type === 'mysql' && 'Example: mysql://user:pass@localhost:3306/mydb'}
            </p>
          </div>
        </>
      )}
    </div>
  );
}
