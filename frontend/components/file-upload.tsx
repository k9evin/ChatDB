'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import config from '@/config';

export function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [dbType, setDbType] = useState<string>('mysql');
  const [tableName, setTableName] = useState<string>('');
  const [databaseName, setDatabaseName] = useState<string>('');
  const { toast } = useToast();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const file = event.target.files[0];
      const fileType = file.name.split('.').pop()?.toLowerCase();
      
      if (dbType === 'mysql' && fileType !== 'csv') {
        toast({
          title: 'Error',
          description: 'Please upload a CSV file for MySQL database',
          variant: 'destructive',
        });
        return;
      }
      
      if (dbType === 'mongodb' && fileType !== 'json') {
        toast({
          title: 'Error',
          description: 'Please upload a JSON file for MongoDB database',
          variant: 'destructive',
        });
        return;
      }
      
      setFile(file);
    }
  };

  const handleUpload = async () => {
    if (!file || !tableName || !databaseName) {
      toast({
        title: 'Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('db_type', dbType);
    formData.append('table_name', tableName);
    formData.append('database_name', databaseName);

    try {
      const response = await fetch(`${config.backendUrl}${config.api.upload}`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        try {
          const data = await response.json();
          toast({
            title: 'Success',
            description: data.message,
          });
        } catch (jsonError) {
          console.error('Error parsing JSON response:', jsonError);
          toast({
            title: 'Error',
            description: 'Failed to parse server response.',
            variant: 'destructive',
          });
        }
      } else {
        try {
          const errorData = await response.json();
          toast({
            title: 'Error',
            description: errorData.detail,
            variant: 'destructive',
          });
        } catch (jsonError) {
          console.error('Error parsing JSON error response:', jsonError);
          toast({
            title: 'Error',
            description: 'Failed to parse server error response.',
            variant: 'destructive',
          });
        }
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      toast({
        title: 'Error',
        description: 'An unexpected error occurred while uploading the file.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="mb-8">
      <h2 className="text-2xl font-semibold mb-4">Upload Data File</h2>
      <div className="space-y-4">
        <div>
          <Label htmlFor="data-file">
            Select File ({dbType === 'mysql' ? 'CSV only' : 'JSON only'})
          </Label>
          <Input
            id="data-file"
            type="file"
            accept={dbType === 'mysql' ? '.csv' : '.json'}
            onChange={handleFileChange}
          />
        </div>
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
          <Label htmlFor="database-name" className="flex items-center gap-1">
            Database Name
            <span className="text-red-500">*</span>
          </Label>
          <Input
            id="database-name"
            value={databaseName}
            onChange={(e) => setDatabaseName(e.target.value)}
            placeholder={`Enter ${dbType === 'mysql' ? 'database' : 'database'} name`}
            required
          />
        </div>
        <div>
          <Label htmlFor="table-name">
            {dbType === 'mysql' ? 'Table Name' : 'Collection Name'}
          </Label>
          <Input
            id="table-name"
            type="text"
            value={tableName}
            onChange={(e) => setTableName(e.target.value)}
            placeholder={`Enter ${dbType === 'mysql' ? 'table' : 'collection'} name`}
          />
        </div>
        <Button onClick={handleUpload} disabled={!file || !tableName || !databaseName}>
          Upload and Process
        </Button>
      </div>
    </div>
  );
}
