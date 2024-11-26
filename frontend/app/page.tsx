import { DatabaseProvider } from '@/contexts/database-context';
import { ChatLayout } from '@/components/chat-layout';
import { Toaster } from '@/components/ui/toaster';

export default function Home() {
  return (
    <DatabaseProvider>
      <ChatLayout />
      <Toaster />
    </DatabaseProvider>
  );
}