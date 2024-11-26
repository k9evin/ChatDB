'use client';

import { useState, useEffect } from 'react';
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

interface DatabaseExplorerProps {
  databaseName?: string;
}

interface SQLResult {
  [key: string]: any;
}

interface MongoResult {
  [key: string]: any;
}

export function DatabaseExplorer({ databaseName }: DatabaseExplorerProps) {
  const [dbType, setDbType] = useState<string>('mysql');
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [sampleData, setSampleData] = useState<SQLResult[] | MongoResult[]>([]);
  const [sampleQueries, setSampleQueries] = useState<any[]>([]);
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState<string>('');
  const [generatedQuery, setGeneratedQuery] = useState<string>('');
  const [queryResults, setQueryResults] = useState<SQLResult[] | MongoResult[]>(
    []
  );
  const { toast } = useToast();
  const [customDatabaseName, setCustomDatabaseName] = useState<string>(
    databaseName || ''
  );
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [selectedConstruct, setSelectedConstruct] = useState<string>('');

  useEffect(() => {
    if (databaseName) {
      setCustomDatabaseName(databaseName);
      fetchTables();
    }
  }, [databaseName]);

  useEffect(() => {
    if (selectedTable) {
      fetchSampleData();
      fetchSampleQueries();
    }
  }, [selectedTable]);

  const fetchTables = async () => {
    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.explore}?db_type=${dbType}&database_name=${customDatabaseName}`
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

  const fetchSampleData = async () => {
    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.sampleData}?db_type=${dbType}&table_name=${selectedTable}&database_name=${customDatabaseName}`
      );
      if (response.ok) {
        const data = await response.json();
        setSampleData(dbType === 'mysql' ? data : data.result || data);
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
      const queryParams = new URLSearchParams({
        db_type: dbType,
        table_name: selectedTable,
        database_name: customDatabaseName,
        ...(selectedConstruct && selectedConstruct !== 'all' && { construct: selectedConstruct })
      });

      const response = await fetch(
        `${config.backendUrl}${config.api.sampleQueries}?${queryParams}`
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
      const response = await fetch(
        `${config.backendUrl}${config.api.naturalLanguageQuery}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: naturalLanguageQuery,
            db_type: dbType,
            table_name: selectedTable,
            database_name: customDatabaseName,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.generated_query) {
          setGeneratedQuery(data.generated_query);
        } else {
          toast({
            title: 'Info',
            description: data.message || 'No query could be generated',
          });
        }
      } else {
        const errorData = await response.json();
        toast({
          title: 'Error',
          description:
            errorData.detail || 'Failed to process natural language query',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error processing natural language query:', error);
      toast({
        title: 'Error',
        description: 'An unexpected error occurred',
        variant: 'destructive',
      });
    }
  };

  const executeQuery = async (query: string) => {
    try {
      const response = await fetch(
        `${config.backendUrl}${config.api.executeQuery}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query,
            db_type: dbType,
            table_name: selectedTable,
            database_name: customDatabaseName,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setQueryResults(data.result);
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

  const renderSampleData = () => {
    if (!sampleData) return 'No sample data available';

    if (dbType === 'mysql') {
      return (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              {sampleData.length > 0 && (
                <tr>
                  {Object.keys(sampleData[0]).map((column) => (
                    <th
                      key={column}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              )}
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sampleData.map((row, i) => (
                <tr key={i}>
                  {Object.values(row).map((value: any, j) => (
                    <td
                      key={j}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                    >
                      {typeof value === 'object'
                        ? JSON.stringify(value)
                        : String(value)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    } else {
      return (
        <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
          {JSON.stringify(sampleData, null, 2)}
        </pre>
      );
    }
  };

  const handleDatabaseSubmit = async () => {
    if (!customDatabaseName) {
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
      setSampleData([]); // Reset sample data
      setSampleQueries([]); // Reset sample queries
    } catch (error) {
      console.error('Error submitting database:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const refreshSampleQueries = async () => {
    try {
      const queryParams = new URLSearchParams({
        db_type: dbType,
        table_name: selectedTable,
        ...(customDatabaseName && { database_name: customDatabaseName }),
        ...(selectedConstruct &&
          selectedConstruct !== 'all' && { construct: selectedConstruct }),
      });

      const response = await fetch(
        `${config.backendUrl}${config.api.sampleQueries}?${queryParams}`
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

  return (
    <div className="space-y-8">
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
              <Label
                htmlFor="database-name"
                className="flex items-center gap-1"
              >
                Database Name
                <span className="text-red-500">*</span>
              </Label>
              <div className="flex gap-2">
                <Input
                  id="database-name"
                  value={customDatabaseName}
                  onChange={(e) => setCustomDatabaseName(e.target.value)}
                  placeholder={`Enter ${
                    dbType === 'mysql' ? 'database' : 'database'
                  } name`}
                  className="flex-1"
                />
                <Button
                  onClick={handleDatabaseSubmit}
                  disabled={!customDatabaseName || isSubmitting}
                >
                  {isSubmitting ? 'Loading...' : 'Submit'}
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

      {selectedTable && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Sample Data</CardTitle>
            </CardHeader>
            <CardContent>{renderSampleData()}</CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                <span>Sample Queries</span>
                <div className="flex gap-2">
                  <Select
                    value={selectedConstruct}
                    onValueChange={setSelectedConstruct}
                  >
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="Select query type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Query Types</SelectItem>
                      <SelectItem value="group by with aggregation">
                        Group By with Sum/Avg
                      </SelectItem>
                      <SelectItem value="group by with count">
                        Group By with Count
                      </SelectItem>
                      <SelectItem value="order by with limit">
                        Order By with Limit
                      </SelectItem>
                      <SelectItem value="where clause">
                        Where Clause
                      </SelectItem>
                      <SelectItem value="having clause">
                        Having Clause
                      </SelectItem>
                      <SelectItem value="select columns">
                        Select Specific Columns
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    onClick={refreshSampleQueries}
                    variant="outline"
                    size="sm"
                  >
                    Refresh
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {sampleQueries.length > 0 ? (
                <ul className="space-y-4">
                  {sampleQueries.map((query, index) => (
                    <li key={index} className="bg-gray-100 p-4 rounded-md">
                      <p className="font-semibold text-gray-700">{query.natural_language}</p>
                      <pre className="mt-2 p-2 bg-gray-50 rounded text-sm overflow-x-auto">
                        {dbType === 'mysql'
                          ? query.mysql_query
                          : query.mongodb_query}
                      </pre>
                      <Button
                        onClick={() =>
                          executeQuery(
                            dbType === 'mysql'
                              ? query.mysql_query
                              : query.mongodb_query
                          )
                        }
                        className="mt-2"
                        size="sm"
                      >
                        Execute
                      </Button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-center py-4">
                  No queries available for the selected type
                </p>
              )}
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
              {dbType === 'mysql' ? (
                <div className="overflow-x-auto">
                  {queryResults && queryResults.length > 0 ? (
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {Object.keys(queryResults[0]).map((column) => (
                            <th
                              key={column}
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              {column}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {queryResults.map((row: any, i: number) => (
                          <tr key={i}>
                            {Object.values(row).map((value: any, j: number) => (
                              <td
                                key={j}
                                className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                              >
                                {typeof value === 'object'
                                  ? JSON.stringify(value)
                                  : String(value)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p>No results available</p>
                  )}
                </div>
              ) : (
                <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                  {queryResults.length > 0
                    ? JSON.stringify(queryResults, null, 2)
                    : 'No results yet'}
                </pre>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
