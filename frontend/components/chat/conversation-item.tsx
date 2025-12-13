'use client';

interface ConversationItemProps {
  id: string;
  title: string;
  isActive: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onRename: (id: string) => void;
}

export function ConversationItem({
  id,
  title,
  isActive,
  onSelect,
  onDelete,
  onRename,
}: ConversationItemProps) {
  return (
    <div
      className={`group relative rounded-lg px-3 py-2.5 text-sm font-medium cursor-pointer transition-colors ${isActive
        ? 'bg-primary/10 text-primary'
        : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
        }`}
      onClick={() => onSelect(id)}
    >
      <div className="truncate pr-8">{title || 'Conversation'}</div>
      {/* Delete button - only show on hover */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(id);
        }}
        className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-destructive/10 rounded text-muted-foreground hover:text-destructive"
        aria-label="Delete conversation"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  );
}
