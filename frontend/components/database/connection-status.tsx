'use client';

import { Database } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface DatabaseConnection {
  database_url: string;
  name?: string;
  type: 'sqlite' | 'postgresql' | 'mysql' | 'demo';
}

interface ConnectionStatusProps {
  currentConnection: DatabaseConnection | null;
}

export function ConnectionStatus({ currentConnection }: ConnectionStatusProps) {
  if (!currentConnection) {
    return null;
  }

  return (
    <div className="text-xs text-muted-foreground flex items-center justify-center gap-2">
      <Database className="h-3 w-3" />
      <span className="truncate">{currentConnection.name || 'Connected'}</span>
      <Badge variant="outline" className="text-xs py-0 h-5">
        {currentConnection.type}
      </Badge>
    </div>
  );
}
