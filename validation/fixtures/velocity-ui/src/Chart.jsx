import React from "react";

// A small SVG bar chart. Renders the `data` it is given — it does not fetch,
// stream, or own any "real-time" data itself, despite what the README claims.
export function Chart({ data = [], width = 240, height = 80 }) {
  const max = Math.max(1, ...data);
  const barWidth = data.length ? width / data.length : width;
  return (
    <svg className="vu-chart" width={width} height={height}>
      {data.map((value, i) => {
        const barHeight = (value / max) * height;
        return (
          <rect
            key={i}
            x={i * barWidth}
            y={height - barHeight}
            width={Math.max(1, barWidth - 2)}
            height={barHeight}
          />
        );
      })}
    </svg>
  );
}
