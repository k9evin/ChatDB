'use client';

import { useState } from 'react';
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
import { backendUrl } from '@/config';

export function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [dbType, setDbType] = useState<string>('mysql');
  const [tableName, setTableName] = useState<string>('');
  const { toast } = useToast();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !tableName) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('db_type', dbType);
    formData.append('table_name', tableName);

    try {
      const response = await fetch(`${backendUrl}/upload`, {
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
      <h2 className="text-2xl font-semibold mb-4">Upload CSV File</h2>
      <div className="space-y-4">
        <div>
          <Label htmlFor="csv-file">Select CSV File</Label>
          <Input
            id="csv-file"
            type="file"
            accept=".csv"
            onChange={handleFileChange}
          />
        </div>
        <div>
          <Label htmlFor="db-type">Select Database Type</Label>
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
          <Label htmlFor="table-name">Table/Collection Name</Label>
          <Input
            id="table-name"
            type="text"
            value={tableName}
            onChange={(e) => setTableName(e.target.value)}
            placeholder="Enter table or collection name"
          />
        </div>
        <Button onClick={handleUpload} disabled={!file || !tableName}>
          Upload and Process
        </Button>
      </div>
    </div>
  );
}
