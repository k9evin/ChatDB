import { Button } from "@/components/ui/button";

interface SampleQueriesListProps {
  queries: any[];
  dbType: string;
  onExecute: (query: string) => void;
}

export function SampleQueriesList({ queries, dbType, onExecute }: SampleQueriesListProps) {
  return (
    <ul className="space-y-4">
      {queries.map((query: any, index: number) => (
        <li key={index} className="bg-gray-100 p-4 rounded-md">
          <p className="font-semibold text-gray-700">{query.natural_language}</p>
          <pre className="mt-2 p-2 bg-gray-50 rounded text-sm overflow-x-auto">
            {dbType === 'mysql' ? query.mysql_query : query.mongodb_query}
          </pre>
          <Button
            onClick={() =>
              onExecute(dbType === 'mysql' ? query.mysql_query : query.mongodb_query)
            }
            className="mt-2"
            size="sm"
          >
            Execute
          </Button>
        </li>
      ))}
    </ul>
  );
} 