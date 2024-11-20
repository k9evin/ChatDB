'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { backendUrl } from '@/config';

export function DatabaseExplorer() {
  const [dbType, setDbType] = useState<string>('mysql');
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [sampleData, setSampleData] = useState<string>('');
  const [sampleQueries, setSampleQueries] = useState<any[]>([]);
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState<string>('');
  const [generatedQuery, setGeneratedQuery] = useState<string>('');
  const [queryResults, setQueryResults] = useState<string>('');
  const { toast } = useToast();

  useEffect(() => {
    fetchTables();
  }, [dbType]);

  useEffect(() => {
    if (selectedTable) {
      fetchSampleData();
      fetchSampleQueries();
    }
  }, [selectedTable]);

  const fetchTables = async () => {
    try {
      const response = await fetch(`${backendUrl}/explore?db_type=${dbType}`);
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

  const fetchSampleData = async () => {
    try {
      const response = await fetch(
        `${backendUrl}/sample-data?db_type=${dbType}&table_name=${selectedTable}`
      );
      if (response.ok) {
        const data = await response.json();
        setSampleData(JSON.stringify(data, null, 2));
      } else {
        toast({
          title: 'Error',
          description: 'Failed to fetch sample data',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error fetching sample data:', error);
    }
  };

  const fetchSampleQueries = async () => {
    try {
      const response = await fetch(
        `${backendUrl}/sample-queries?db_type=${dbType}&table_name=${selectedTable}`
      );
      if (response.ok) {
        const data = await response.json();
        setSampleQueries(data.sample_queries);
      } else {
        toast({
          title: 'Error',
          description: 'Failed to fetch sample queries',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error fetching sample queries:', error);
    }
  };

  const handleNaturalLanguageQuery = async () => {
    try {
      const response = await fetch(`${backendUrl}/natural-language-query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: naturalLanguageQuery,
          db_type: dbType,
          table_name: selectedTable,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedQuery(data.generated_query);
      } else {
        toast({
          title: 'Error',
          description: 'Failed to process natural language query',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error processing natural language query:', error);
    }
  };

  const executeQuery = async (query: string) => {
    try {
      const response = await fetch(`${backendUrl}/execute-query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          db_type: dbType,
          table_name: selectedTable,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setQueryResults(JSON.stringify(data.result, null, 2));
      } else {
        toast({
          title: 'Error',
          description: 'Failed to execute query',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error executing query:', error);
    }
  };

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle>Database Explorer</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label
                htmlFor="db-type"
                className="block text-sm font-medium text-gray-700"
              >
                Select Database Type
              </label>
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
              <label
                htmlFor="table-select"
                className="block text-sm font-medium text-gray-700"
              >
                Select Table/Collection
              </label>
              <Select value={selectedTable} onValueChange={setSelectedTable}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select table/collection" />
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
          </div>
        </CardContent>
      </Card>

      {selectedTable && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Sample Data</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                {sampleData || 'No sample data available'}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sample Queries</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {sampleQueries.map((query, index) => (
                  <li key={index} className="bg-gray-100 p-2 rounded-md">
                    <p className="font-semibold">{query.natural_language}</p>
                    <pre className="text-sm mt-1">{query.sql_query}</pre>
                    <Button
                      onClick={() => executeQuery(query.sql_query)}
                      className="mt-2"
                      size="sm"
                    >
                      Execute
                    </Button>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Natural Language Query</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Input
                  value={naturalLanguageQuery}
                  onChange={(e) => setNaturalLanguageQuery(e.target.value)}
                  placeholder="Enter your query in natural language"
                />
                <Button onClick={handleNaturalLanguageQuery}>
                  Generate Query
                </Button>
                {generatedQuery && (
                  <div>
                    <h4 className="font-semibold">Generated Query:</h4>
                    <pre className="bg-gray-100 p-2 rounded-md mt-2">
                      {generatedQuery}
                    </pre>
                    <Button
                      onClick={() => executeQuery(generatedQuery)}
                      className="mt-2"
                      size="sm"
                    >
                      Execute
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Query Results</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                {queryResults || 'No results yet'}
              </pre>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
