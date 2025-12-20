import { ChatLayout } from '@/components/chat-layout';
import { Toaster } from '@/components/ui/toaster';
import { ThemeProvider } from '@/components/theme-provider';
import { DatabaseProvider } from '@/contexts/database-context';

export default function Home() {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="light"
      enableSystem={false}
      disableTransitionOnChange
    >
      <DatabaseProvider>
        <ChatLayout />
        <Toaster />
      </DatabaseProvider>
    </ThemeProvider>
  );
}
