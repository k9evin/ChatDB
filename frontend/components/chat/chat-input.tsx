'use client';

import { Loader2, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ShineBorder } from '@/components/ui/shine-border';

interface ChatInputProps {
    input: string;
    setInput: (value: string) => void;
    onSubmit: () => void;
    isConnected: boolean;
    isStreaming: boolean;
}

export function ChatInput({ input, setInput, onSubmit, isConnected, isStreaming }: ChatInputProps) {
    return (
        <div className="w-full relative shadow-[0_8px_30px_rgb(0,0,0,0.05)] focus-within:shadow-[0_8px_30px_rgb(0,200,83,0.1)] transition-all duration-300 rounded-2xl overflow-hidden">
            <ShineBorder
                className="dark:block hidden"
                shineColor={["#22c55e", "#4ade80", "#86efac"]}
                duration={10}
                borderWidth={4}
            />
            <form
                onSubmit={(e) => {
                    e.preventDefault();
                    onSubmit();
                }}
                className="flex flex-col relative z-10 w-full bg-background border-2 border-primary/50 dark:border-transparent rounded-2xl"
            >
                <div className="px-5 pt-5 pb-2">
                    <Textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                onSubmit();
                            }
                        }}
                        placeholder="Ask me anything..."
                        className="min-h-[52px] max-h-[200px] w-full border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 resize-none text-sm placeholder:text-muted-foreground/50 text-foreground p-0 rounded-none custom-scrollbar"
                        disabled={!isConnected || isStreaming}
                        aria-label="Message input"
                        id="chat-input"
                    />
                </div>

                <div className="flex items-center justify-between px-4 pb-4 mt-2">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground/50">
                        {/* Intentionally left empty to remove dummy buttons */}
                    </div>

                    <div className="flex items-center gap-4">
                        <Button
                            type="submit"
                            disabled={!isConnected || isStreaming || !input.trim()}
                            className="h-8 w-8 p-0 rounded-lg bg-transparent hover:bg-muted text-foreground hover:text-primary transition-colors"
                        >
                            {isStreaming ? (
                                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                            ) : (
                                <Send className="h-5 w-5" />
                            )}
                        </Button>
                    </div>
                </div>
            </form>
        </div>
    );
}
