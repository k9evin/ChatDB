'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface DatabaseContextType {
  dbType: string;
  databaseName: string;
  databaseUrl: string | null;
  setDbType: (type: string) => void;
  setDatabaseName: (name: string) => void;
  setDatabaseUrl: (url: string | null) => void;
}

const DatabaseContext = createContext<DatabaseContextType | undefined>(undefined);

export function DatabaseProvider({ children }: { children: ReactNode }) {
  const [dbType, setDbType] = useState<string>('mysql');
  const [databaseName, setDatabaseName] = useState<string>('');
  const [databaseUrl, setDatabaseUrl] = useState<string | null>(null);

  return (
    <DatabaseContext.Provider
      value={{
        dbType,
        databaseName,
        databaseUrl,
        setDbType,
        setDatabaseName,
        setDatabaseUrl,
      }}
    >
      {children}
    </DatabaseContext.Provider>
  );
}

export function useDatabase() {
  const context = useContext(DatabaseContext);
  if (context === undefined) {
    throw new Error('useDatabase must be used within a DatabaseProvider');
  }
  return context;
} 