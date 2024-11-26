'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface DatabaseContextType {
  dbType: string;
  selectedTable: string;
  databaseName: string;
  setDbType: (type: string) => void;
  setSelectedTable: (table: string) => void;
  setDatabaseName: (name: string) => void;
}

const DatabaseContext = createContext<DatabaseContextType | undefined>(undefined);

export function DatabaseProvider({ children }: { children: ReactNode }) {
  const [dbType, setDbType] = useState<string>('mysql');
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [databaseName, setDatabaseName] = useState<string>('');

  return (
    <DatabaseContext.Provider
      value={{
        dbType,
        selectedTable,
        databaseName,
        setDbType,
        setSelectedTable,
        setDatabaseName,
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