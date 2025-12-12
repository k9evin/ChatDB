/**
 * Lightweight local persistence using localStorage (stringified JSON).
 * Keeps conversations indexed by ID with a separate index list for metadata.
 */

export interface StoredMessage {
  type: "user" | "assistant";
  content: string;
  chartData?: any;
  tableData?: any[];
}

export interface ConversationMeta {
  id: string;
  title: string;
  updatedAt: number;
  createdAt: number;
  databaseUrl?: string | null;
}

export interface ConversationRecord extends ConversationMeta {
  messages: StoredMessage[];
}

const INDEX_KEY = "chatdb:conversations:index";
const CONVO_KEY = (id: string) => `chatdb:conversation:${id}`;

function readJSON<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJSON<T>(key: string, value: T) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore quota errors
  }
}

async function loadIndex(): Promise<ConversationMeta[]> {
  return readJSON<ConversationMeta[]>(INDEX_KEY, []);
}

async function saveIndex(list: ConversationMeta[]) {
  writeJSON(INDEX_KEY, list);
}

export async function listConversations(): Promise<ConversationMeta[]> {
  return loadIndex();
}

export async function loadConversation(
  id: string
): Promise<ConversationRecord | null> {
  const convo = readJSON<ConversationRecord | null>(CONVO_KEY(id), null);
  return convo;
}

export async function saveConversation(convo: ConversationRecord) {
  const index = await loadIndex();
  const existingIdx = index.findIndex((c) => c.id === convo.id);
  const meta: ConversationMeta = {
    id: convo.id,
    title: convo.title,
    createdAt: convo.createdAt,
    updatedAt: convo.updatedAt,
    databaseUrl: convo.databaseUrl,
  };
  if (existingIdx >= 0) {
    index[existingIdx] = meta;
  } else {
    index.unshift(meta);
  }
  await saveIndex(index);
  writeJSON(CONVO_KEY(convo.id), convo);
}

export async function deleteConversation(id: string) {
  const index = await loadIndex();
  const filtered = index.filter((c) => c.id !== id);
  await saveIndex(filtered);
  try {
    localStorage.removeItem(CONVO_KEY(id));
  } catch {
    // ignore
  }
}



