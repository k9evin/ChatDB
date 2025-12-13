'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import config from '@/config';
import { useDatabase } from '@/contexts/database-context';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  className?: string;
}

export function FileUpload({ className }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [tableName, setTableName] = useState<string>('');
  const { toast } = useToast();
  const { databaseUrl } = useDatabase();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const file = event.target.files[0];
      const fileType = file.name.split('.').pop()?.toLowerCase();

      if (fileType !== 'csv') {
        toast({
          title: 'Error',
          description: 'Please upload a CSV file',
          variant: 'destructive',
        });
        return;
      }

      setFile(file);
    }
  };

  const handleUpload = async () => {
    if (!file || !tableName) {
      toast({
        title: 'Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      });
      return;
    }

    if (!databaseUrl) {
      toast({
        title: 'Error',
        description: 'Please configure a database connection first',
        variant: 'destructive',
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('table_name', tableName);
    formData.append('database_url', databaseUrl);

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
            description: `Imported ${data.rows_imported} rows into ${data.table_name}`,
            variant: 'success',
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
    <Card className={cn('shadow-none', className)}>
      <CardHeader>
        <CardTitle>Upload Data File</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <Label htmlFor="data-file">Select CSV File</Label>
            <Input id="data-file" type="file" accept=".csv" onChange={handleFileChange} />
          </div>
          <div>
            <Label htmlFor="database-name">Table Name</Label>
            <Input
              id="database-name"
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              placeholder="Enter target table name"
              required
            />
          </div>
          <Button onClick={handleUpload} disabled={!file || !tableName} className="w-full">
            Upload and Process
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
