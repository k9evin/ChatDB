import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface DataTableProps {
  data: any[];
  dbType: string;
}

export function DataTable({ data, dbType }: DataTableProps) {
  if (!data || data.length === 0) {
    return <div className="text-sm text-muted-foreground py-4 text-center">No data available</div>;
  }

  // Get all unique keys from all rows to handle cases where rows have different keys
  const allKeys: string[] = [];
  data.forEach((row) => {
    Object.keys(row).forEach((key) => {
      if (!allKeys.includes(key)) {
        allKeys.push(key);
      }
    });
  });
  const columns = allKeys;

  return (
    <div className="rounded-md border overflow-hidden min-w-0">
      <div className="overflow-x-auto w-full">
        <Table className="min-w-full">
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column} className="font-semibold">
                  {column}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row: any, i: number) => (
              <TableRow key={i}>
                {columns.map((column, j: number) => {
                  const value = row[column];
                  return (
                    <TableCell key={j} className="font-mono text-sm whitespace-nowrap">
                      {value === null || value === undefined ? (
                        <span className="text-muted-foreground italic">null</span>
                      ) : typeof value === 'object' ? (
                        JSON.stringify(value)
                      ) : (
                        String(value)
                      )}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
