'use client';

import * as React from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts';
import {
  type ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';

interface ChartVisualizationProps {
  chartType: string;
  data: any[];
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

const COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))',
];

export function ChartVisualization({ chartType, data, config }: ChartVisualizationProps) {
  if (!data || data.length === 0) {
    return <div className="text-muted-foreground">No data to display</div>;
  }

  const chartConfig: ChartConfig = {};

  // Build chart config based on data keys
  if (config.y_key) {
    chartConfig[config.y_key] = {
      label: config.y_label || config.y_key,
      color: 'hsl(var(--chart-1))',
    };
  }

  if (config.multiple_series) {
    config.multiple_series.forEach((key, index) => {
      chartConfig[key] = {
        label: key,
        color: COLORS[index % COLORS.length],
      };
    });
  }

  switch (chartType) {
    case 'bar':
      return (
        <div className="space-y-4">
          {config.title && <h3 className="text-lg font-semibold">{config.title}</h3>}
          <ChartContainer config={chartConfig} className="h-[400px]">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey={config.x_key}
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <ChartLegend content={<ChartLegendContent />} />
              {config.multiple_series ? (
                config.multiple_series.map((key) => (
                  <Bar key={key} dataKey={key} fill={`var(--color-${key})`} radius={[4, 4, 0, 0]} />
                ))
              ) : config.y_key ? (
                <Bar dataKey={config.y_key} fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
              ) : null}
            </BarChart>
          </ChartContainer>
        </div>
      );

    case 'line':
      return (
        <div className="space-y-4">
          {config.title && <h3 className="text-lg font-semibold">{config.title}</h3>}
          <ChartContainer config={chartConfig} className="h-[400px]">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey={config.x_key}
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <ChartLegend content={<ChartLegendContent />} />
              {config.multiple_series ? (
                config.multiple_series.map((key) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={`var(--color-${key})`}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                ))
              ) : config.y_key ? (
                <Line
                  type="monotone"
                  dataKey={config.y_key}
                  stroke="hsl(var(--chart-1))"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              ) : null}
            </LineChart>
          </ChartContainer>
        </div>
      );

    case 'area':
      return (
        <div className="space-y-4">
          {config.title && <h3 className="text-lg font-semibold">{config.title}</h3>}
          <ChartContainer config={chartConfig} className="h-[400px]">
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey={config.x_key}
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <ChartLegend content={<ChartLegendContent />} />
              {config.multiple_series ? (
                config.multiple_series.map((key, index) => (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={`var(--color-${key})`}
                    fill={`var(--color-${key})`}
                    fillOpacity={0.6}
                  />
                ))
              ) : config.y_key ? (
                <Area
                  type="monotone"
                  dataKey={config.y_key}
                  stroke="hsl(var(--chart-1))"
                  fill="hsl(var(--chart-1))"
                  fillOpacity={0.6}
                />
              ) : null}
            </AreaChart>
          </ChartContainer>
        </div>
      );

    case 'pie':
      return (
        <div className="space-y-4">
          {config.title && <h3 className="text-lg font-semibold">{config.title}</h3>}
          <ChartContainer config={chartConfig} className="h-[400px]">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey={config.value_key || 'value'}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <ChartTooltip content={<ChartTooltipContent />} />
            </PieChart>
          </ChartContainer>
        </div>
      );

    case 'scatter':
      return (
        <div className="space-y-4">
          {config.title && <h3 className="text-lg font-semibold">{config.title}</h3>}
          <ChartContainer config={chartConfig} className="h-[400px]">
            <ResponsiveContainer>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={config.x_key} tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <ChartTooltip content={<ChartTooltipContent />} />
                {config.y_key && <Bar dataKey={config.y_key} fill="hsl(var(--chart-1))" />}
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </div>
      );

    default:
      return (
        <div className="text-muted-foreground">Chart type {`"${chartType}"`} is not supported</div>
      );
  }
}
