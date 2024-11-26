interface DataTableProps {
  data: any[];
  dbType: string;
}

export function DataTable({ data, dbType }: DataTableProps) {
  if (!data || data.length === 0) return null;

  if (dbType === 'mysql') {
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {Object.keys(data[0]).map((column) => (
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
            {data.map((row: any, i: number) => (
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
      </div>
    );
  }

  return (
    <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
} 