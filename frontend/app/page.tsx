'use client';

import { ChatLayout } from '@/components/chat-layout';
import { Toaster } from '@/components/ui/toaster';
import { DatabaseProvider } from '@/contexts/database-context';

export default function Home() {
  return (
    <DatabaseProvider>
      <ChatLayout />
      <Toaster />
    </DatabaseProvider>
  );
}
