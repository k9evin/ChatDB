'use client';

import { Database, Moon, Plus, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader } from '@/components/ui/sidebar';
import type { ConversationMeta } from '@/lib/conversation-store';
import { DatabaseConnection } from '../database-connection';
import { ConversationItem } from './conversation-item';

interface ConversationSidebarProps {
    conversations: ConversationMeta[];
    isLoadingConversations: boolean;
    conversationId: string | null;
    onNewConversation: () => void;
    onSelectConversation: (id: string) => void;
    onDeleteConversation: (id: string) => void;
    onRenameConversation: (id: string) => void;
}

export function ConversationSidebar({
    conversations,
    isLoadingConversations,
    conversationId,
    onNewConversation,
    onSelectConversation,
    onDeleteConversation,
    onRenameConversation,
}: ConversationSidebarProps) {
    const { theme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    // Avoid hydration mismatch
    useEffect(() => {
        setMounted(true);
    }, []);

    return (
        <Sidebar className="h-full w-[260px] border-r border-border bg-sidebar flex flex-col">
            <SidebarHeader className="px-5 pt-6 pb-4">
                <div className="flex items-center gap-3">
                    <div className="bg-primary/10 p-2 rounded-xl">
                        <Database className="h-5 w-5 text-primary" />
                    </div>
                    <p className="text-xl font-bold tracking-tight text-foreground">ChatDB</p>
                </div>
            </SidebarHeader>

            <SidebarContent className="flex flex-col px-3 gap-4 flex-1 min-h-0">
                {/* New Chat Button */}
                <button
                    onClick={onNewConversation}
                    className="flex items-center gap-2 w-full px-4 py-3 bg-primary text-primary-foreground hover:bg-primary/90 text-sm font-medium rounded-xl transition-all shadow-sm shadow-primary/20"
                >
                    <Plus className="h-4 w-4" />
                    <span>New chat</span>
                </button>

                <div className="flex-1 flex flex-col gap-2 min-h-0 overflow-y-auto no-scrollbar pt-2">
                    <div className="px-3">
                        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">
                            Recent
                        </h3>
                    </div>

                    <div className="space-y-1">
                        {isLoadingConversations ? (
                            <div className="px-3 py-2 text-xs text-muted-foreground">Loading...</div>
                        ) : conversations.length === 0 ? (
                            <div className="px-3 py-2 text-xs text-muted-foreground italic">No history yet</div>
                        ) : (
                            conversations.map((convo) => (
                                <ConversationItem
                                    key={convo.id}
                                    id={convo.id}
                                    title={convo.title}
                                    isActive={conversationId === convo.id}
                                    onSelect={onSelectConversation}
                                    onDelete={onDeleteConversation}
                                    onRename={onRenameConversation}
                                />
                            ))
                        )}
                    </div>
                </div>
            </SidebarContent>

            <SidebarFooter className="p-4 flex flex-col gap-4 mt-auto border-t border-border/40 bg-sidebar">
                <DatabaseConnection />

                {/* Theme Toggle */}
                {mounted && (
                    <div className="bg-background/50 border border-border rounded-lg p-1 flex">
                        <button
                            onClick={() => setTheme('light')}
                            className={`flex-1 flex items-center justify-center gap-2 py-1.5 text-sm font-medium rounded-md transition-all ${theme === 'light' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'}`}
                            title="Light"
                        >
                            <Sun className={`h-4 w-4 ${theme === 'light' ? 'fill-current' : ''}`} />
                        </button>
                        <button
                            onClick={() => setTheme('dark')}
                            className={`flex-1 flex items-center justify-center gap-2 py-1.5 text-sm font-medium rounded-md transition-all ${theme === 'dark' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'}`}
                            title="Dark"
                        >
                            <Moon className={`h-4 w-4 ${theme === 'dark' ? 'fill-current' : ''}`} />
                        </button>
                        <button
                            onClick={() => setTheme('system')}
                            className={`flex-1 flex items-center justify-center gap-2 py-1.5 text-xs font-medium rounded-md transition-all ${theme === 'system' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'}`}
                            title="System"
                        >
                            Auto
                        </button>
                    </div>
                )}
            </SidebarFooter>
        </Sidebar>
    );
}
