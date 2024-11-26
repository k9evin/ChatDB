'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import config from '@/config';
import { useDatabase } from '@/contexts/database-context';
import { cn } from '@/lib/utils';

interface DatabaseExplorerProps {
  className?: string;
}

export function DatabaseExplorer({ className }: DatabaseExplorerProps) {
  const {
    dbType,
    selectedTable,
    databaseName,
    setDbType,
    setSelectedTable,
    setDatabaseName
  } = useDatabase();
  const [tables, setTables] = useState<string[]>([]);
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const fetchTables = async () => {
    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.explore}?db_type=${dbType}&database_name=${databaseName}`
      );
      if (response.ok) {
        const data = await response.json();
        setTables(data.tables || data.collections);
      } else {
        toast({
          title: 'Error',
          description: 'Failed to fetch tables/collections',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error fetching tables:', error);
    }
  };

  const handleDatabaseSubmit = async () => {
    if (!databaseName) {
      toast({
        title: 'Error',
        description: 'Please enter a database name',
        variant: 'destructive',
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await fetchTables();
      setSelectedTable(''); // Reset table selection
      toast({
        title: 'Success',
        description: 'Database connected successfully',
        variant: 'success',
      });
    } catch (error) {
      console.error('Error submitting database:', error);
      toast({
        title: 'Error',
        description: 'Failed to connect to database',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={cn("flex flex-col", className)}>
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Database Explorer</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="db-type">Database Type</Label>
                <Select value={dbType} onValueChange={setDbType}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select database type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mysql">MySQL</SelectItem>
                    <SelectItem value="mongodb">MongoDB</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="database-name">
                  Database Name
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="database-name"
                    value={databaseName}
                    onChange={(e) => setDatabaseName(e.target.value)}
                    placeholder={`Enter ${
                      dbType === 'mysql' ? 'database' : 'database'
                    } name`}
                    className="flex-1"
                  />
                  <Button
                    onClick={handleDatabaseSubmit}
                    disabled={!databaseName || isSubmitting}
                  >
                    {isSubmitting ? 'Loading...' : 'Connect'}
                  </Button>
                </div>
              </div>

              {tables.length > 0 && (
                <div>
                  <Label htmlFor="table-select">
                    {dbType === 'mysql' ? 'Table' : 'Collection'}
                  </Label>
                  <Select value={selectedTable} onValueChange={setSelectedTable}>
                    <SelectTrigger className="w-full">
                      <SelectValue
                        placeholder={`Select ${
                          dbType === 'mysql' ? 'table' : 'collection'
                        }`}
                      />
                    </SelectTrigger>
                    <SelectContent>
                      {tables.map((table) => (
                        <SelectItem key={table} value={table}>
                          {table}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
