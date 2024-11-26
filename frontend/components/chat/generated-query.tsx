import { Button } from "@/components/ui/button";

interface GeneratedQueryProps {
  query: string;
  onExecute: (query: string) => void;
}

export function GeneratedQuery({ query, onExecute }: GeneratedQueryProps) {
  return (
    <div>
      <p className="mb-4">I've generated this query based on your request:</p>
      <pre className="bg-gray-100 p-2 rounded-md mt-2 mb-4">
        {query}
      </pre>
      <Button onClick={() => onExecute(query)}>Execute</Button>
    </div>
  );
} 