'use client';

import { useCallback, useEffect, useState } from 'react';
import { useDatabase } from '@/contexts/database-context';
import {
  type ConversationMeta,
  deleteConversation,
  listConversations,
  loadConversation,
  type StoredMessage,
  saveConversation,
} from '@/lib/conversation-store';

interface ChartData {
  chart_type: string;
  data: any[];
  vega_lite_spec?: any;
  config: {
    x_key?: string;
    y_key?: string;
    data_key?: string;
    value_key?: string;
    title?: string;
    x_label?: string;
    y_label?: string;
    multiple_series?: string[];
  };
}

export interface Message {
  type: 'user' | 'assistant';
  content: string | React.ReactNode;
  chartData?: ChartData;
  tableData?: any[];
}

export function useConversation() {
  const { setDatabaseUrl } = useDatabase();
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationMeta[]>([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);

  const serializeMessage = useCallback(
    (msg: Message): StoredMessage => ({
      type: msg.type,
      content: typeof msg.content === 'string' ? msg.content : '',
      chartData: msg.chartData,
      tableData: msg.tableData,
    }),
    []
  );

  const refreshConversations = useCallback(
    async (preferId?: string | null, skipMessageUpdate = false) => {
      setIsLoadingConversations(true);
      const list = await listConversations();
      setConversations(list);
      const targetId = preferId || list[0]?.id || null;
      if (targetId) {
        const convo = await loadConversation(targetId);
        if (convo) {
          setConversationId(targetId);
          // Only update messages if not streaming (to prevent losing in-progress messages)
          if (!skipMessageUpdate) {
            // Note: We don't update messages here anymore since it's handled by the parent component
          }
          setDatabaseUrl(convo.databaseUrl || null);
        }
      }
      setIsLoadingConversations(false);
    },
    [setDatabaseUrl]
  );

  useEffect(() => {
    refreshConversations();
  }, [refreshConversations]);

  const persistConversation = useCallback(
    async (updatedMessages: Message[], id?: string | null, skipRefresh = false) => {
      // Use provided id, or existing conversationId, or create new one
      // Only create new conversation if id is explicitly null/undefined AND conversationId is also null
      const convId =
        id !== undefined && id !== null
          ? id
          : conversationId ||
            (typeof crypto !== 'undefined' && crypto.randomUUID
              ? crypto.randomUUID()
              : `${Date.now()}`);

      // Load existing conversation to preserve createdAt if it exists
      const existing = convId ? await loadConversation(convId) : null;
      const createdAt = existing?.createdAt || Date.now();

      const firstUser = updatedMessages.find((m) => m.type === 'user');
      const title =
        firstUser && typeof firstUser.content === 'string'
          ? firstUser.content.slice(0, 60)
          : existing?.title || 'Conversation';
      const now = Date.now();
      const record = {
        id: convId,
        title,
        createdAt,
        updatedAt: now,
        databaseUrl: existing?.databaseUrl, // Preserve existing database URL
        messages: updatedMessages.map(serializeMessage),
      };
      await saveConversation(record);
      setConversationId(convId);
      // Only refresh conversations list if not explicitly skipped
      if (!skipRefresh) {
        await refreshConversations(convId, true); // Skip message update to preserve current state
      }
    },
    [conversationId, refreshConversations, serializeMessage]
  );

  const handleSelectConversation = useCallback(
    async (id: string) => {
      const convo = await loadConversation(id);
      if (convo) {
        setConversationId(id);
        setDatabaseUrl(convo.databaseUrl || null);
        return convo.messages as Message[];
      }
      return [];
    },
    [setDatabaseUrl]
  );

  const handleDeleteConversation = useCallback(
    async (id: string) => {
      await deleteConversation(id);
      if (conversationId === id) {
        setConversationId(null);
      }
      await refreshConversations();
    },
    [conversationId, refreshConversations]
  );

  const handleNewConversation = useCallback(() => {
    setConversationId(null);
  }, []);

  const handleRenameConversation = useCallback(
    async (id: string) => {
      const current = conversations.find((c) => c.id === id);
      const nextTitle = window.prompt('Conversation name', current?.title || 'Conversation');
      if (!nextTitle) return;
      const convo = await loadConversation(id);
      if (convo) {
        const updated = { ...convo, title: nextTitle, updatedAt: Date.now() };
        await saveConversation(updated);
        await refreshConversations(id);
      }
    },
    [conversations, refreshConversations]
  );

  return {
    conversationId,
    conversations,
    isLoadingConversations,
    refreshConversations,
    persistConversation,
    handleSelectConversation,
    handleDeleteConversation,
    handleNewConversation,
    handleRenameConversation,
  };
}
