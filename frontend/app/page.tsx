import { FileUpload } from '@/components/file-upload';
import { DatabaseExplorer } from '@/components/database-explorer';
import { Toaster } from "@/components/ui/toaster"

export default function Home() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold mb-8 text-center">ChatDB Website</h1>
      <FileUpload />
      <DatabaseExplorer />
      <Toaster />
    </div>
  );
}