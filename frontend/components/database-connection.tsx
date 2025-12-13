'use client';

import { Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useDatabaseConnection } from '@/hooks/useDatabaseConnection';
import { ConnectionConfig } from './database/connection-config';
import { ConnectionStatus } from './database/connection-status';
import { ConnectionTest } from './database/connection-test';

export function DatabaseConnection() {
  const {
    isOpen,
    setIsOpen,
    connection,
    setConnection,
    currentConnection,
    handleConnect,
    handleUseDemo,
  } = useDatabaseConnection();

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

          <ConnectionConfig
            connection={connection}
            onConnectionChange={setConnection}
            onUseDemo={handleUseDemo}
          />

          <ConnectionTest
            connection={connection}
            onTestResult={() => {}} // Test results are handled internally
          />

          <div className="flex gap-2">
            <Button onClick={handleConnect} className="flex-1">
              Connect
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <ConnectionStatus currentConnection={currentConnection} />
    </div>
  );
}
