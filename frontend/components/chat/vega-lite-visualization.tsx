'use client';

import * as React from 'react';
import { VegaEmbed } from 'react-vega';

type VegaLiteVisualizationProps = {
  spec: Record<string, any>;
};

export function VegaLiteVisualization({ spec }: VegaLiteVisualizationProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = React.useState(600);

  // Measure container width for responsive chart
  React.useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        // Get the actual available width (accounting for padding)
        const width = containerRef.current.offsetWidth;
        // Subtract padding (p-4 = 16px on each side = 32px total)
        const availableWidth = Math.max(width - 32, 300);
        setContainerWidth(availableWidth);
      }
    };

    // Use ResizeObserver for more accurate width tracking
    const resizeObserver = new ResizeObserver(() => {
      updateWidth();
    });

    if (containerRef.current) {
      updateWidth();
      resizeObserver.observe(containerRef.current);
    }

    window.addEventListener('resize', updateWidth);
    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('resize', updateWidth);
    };
  }, []);

  if (!spec) return null;

  // Enhance the spec with responsive width and better styling
  const enhancedSpec = {
    ...spec,
    width: containerWidth,
    height: 300,
    autosize: { 
      type: 'fit', 
      contains: 'padding',
      resize: true
    },
    config: {
      ...spec.config,
      background: 'transparent',
      view: { stroke: 'transparent' },
      axis: {
        labelColor: '#888',
        titleColor: '#aaa',
        gridColor: '#333',
        domainColor: '#555',
      },
      title: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
      },
      line: {
        strokeWidth: 2,
        color: '#60a5fa', // Tailwind blue-400
      },
      point: {
        size: 60,
        filled: true,
        fill: '#60a5fa',
      },
    },
  };

  return (
    <div ref={containerRef} className="w-full min-w-0 p-4 bg-gray-900/50 rounded-lg border border-gray-700 overflow-hidden">
      <VegaEmbed
        spec={enhancedSpec as any}
        options={{
          actions: false,
          renderer: 'canvas',
        }}
      />
    </div>
  );
}


