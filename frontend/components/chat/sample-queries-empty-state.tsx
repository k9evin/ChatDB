'use client';

import { BarChart3, Package, ShoppingCart, Sparkles, TrendingUp, Users } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface SampleQuery {
  id: string;
  title: string;
  description: string;
  query: string;
  icon: React.ReactNode;
  gradient: string;
}

interface SampleQueriesEmptyStateProps {
  onQueryClick: (query: string) => void;
}

export function SampleQueriesEmptyState({ onQueryClick }: SampleQueriesEmptyStateProps) {
  const sampleQueries: SampleQuery[] = [
    {
      id: 'revenue-analysis',
      title: 'Revenue Analysis',
      description: 'Show me total revenue by month with a trend chart',
      query: 'Show me the total revenue by month with a trend chart',
      icon: <TrendingUp className="h-5 w-5" />,
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      id: 'top-customers',
      title: 'Top Customers',
      description: 'Who are the top 5 customers by total spending?',
      query: 'Who are the top 5 customers by total spending?',
      icon: <Users className="h-5 w-5" />,
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      id: 'product-performance',
      title: 'Product Performance',
      description: 'Show me product sales distribution by category',
      query: 'Show me product sales distribution by category with a pie chart',
      icon: <Package className="h-5 w-5" />,
      gradient: 'from-orange-500 to-red-500',
    },
    {
      id: 'order-status',
      title: 'Order Status',
      description: 'What is the breakdown of orders by status?',
      query: 'What is the breakdown of orders by status?',
      icon: <ShoppingCart className="h-5 w-5" />,
      gradient: 'from-green-500 to-emerald-500',
    },
    {
      id: 'inventory-check',
      title: 'Inventory Check',
      description: 'Which products are running low on stock?',
      query: 'Which products have stock below 30 units?',
      icon: <BarChart3 className="h-5 w-5" />,
      gradient: 'from-indigo-500 to-blue-500',
    },
    {
      id: 'customer-growth',
      title: 'Customer Growth',
      description: 'Show customer registration trend over time',
      query: 'Show me customer registration trend by month with a line chart',
      icon: <Sparkles className="h-5 w-5" />,
      gradient: 'from-pink-500 to-rose-500',
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full px-4 py-12">
      {/* Header Section */}
      <div className="text-center mb-12 max-w-2xl">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6">
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-primary">AI-Powered Database Assistant</span>
        </div>

        <h1 className="text-4xl font-semibold mb-4 text-[#111827] dark:text-white tracking-tight">
          What would you like to explore?
        </h1>

        <p className="text-lg font-normal text-[#6B7280] dark:text-gray-400">
          Try one of these sample queries to see ChatDB in action, or ask your own question below
        </p>
      </div>

      {/* Sample Queries Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-6xl w-full">
        {sampleQueries.map((sample) => (
          <Card
            key={sample.id}
            className="group cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-[1.02] border border-border bg-card hover:border-primary/50"
            onClick={() => onQueryClick(sample.query)}
          >
            <CardContent className="p-6">
              {/* Icon with gradient background */}
              <div
                className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br ${sample.gradient} text-white mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}
              >
                {sample.icon}
              </div>

              {/* Title */}
              <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
                {sample.title}
              </h3>

              {/* Description */}
              <p className="text-sm text-muted-foreground leading-relaxed">{sample.description}</p>

              {/* Hover indicator */}
              <div className="mt-4 flex items-center gap-2 text-xs font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Click to try</span>
                <svg
                  className="w-4 h-4 group-hover:translate-x-1 transition-transform"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Footer hint */}
      <div className="mt-12 text-center">
        <p className="text-sm text-muted-foreground">
          💡 <span className="font-medium">Pro tip:</span> You can ask questions in natural
          language, and I'll handle the SQL for you
        </p>
      </div>
    </div>
  );
}
