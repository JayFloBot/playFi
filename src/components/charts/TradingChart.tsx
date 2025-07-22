import React, { useMemo } from 'react';
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Bar,
  ReferenceLine,
} from 'recharts';
import { format } from 'date-fns';
import type { ChartData } from '@/types';
import { formatCurrency, formatNumber } from '@/lib/utils';

interface TradingChartProps {
  data: ChartData[];
  showIndicators?: {
    sma20?: boolean;
    sma50?: boolean;
    rsi?: boolean;
    macd?: boolean;
    volume?: boolean;
    vwap?: boolean;
  };
  entryPoints?: number[];
  exitPoints?: number[];
  height?: number;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-background border rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold">{format(new Date(label), 'MMM dd, yyyy HH:mm')}</p>
        <div className="grid grid-cols-2 gap-2 mt-2">
          <div>
            <p className="text-muted-foreground">Open: <span className="text-foreground">{formatCurrency(data.open)}</span></p>
            <p className="text-muted-foreground">High: <span className="text-green-600">{formatCurrency(data.high)}</span></p>
          </div>
          <div>
            <p className="text-muted-foreground">Close: <span className="text-foreground">{formatCurrency(data.close)}</span></p>
            <p className="text-muted-foreground">Low: <span className="text-red-600">{formatCurrency(data.low)}</span></p>
          </div>
        </div>
        <p className="text-muted-foreground mt-1">Volume: <span className="text-foreground">{formatNumber(data.volume, 0)}</span></p>
        {data.indicators?.rsi && (
          <p className="text-muted-foreground">RSI: <span className="text-foreground">{formatNumber(data.indicators.rsi)}</span></p>
        )}
      </div>
    );
  }
  return null;
};

const CandlestickBar = (props: any) => {
  const { payload, x, y, width, height } = props;
  const { open, close, high, low } = payload;
  
  const isGreen = close > open;
  const color = isGreen ? '#22c55e' : '#ef4444';
  const bodyHeight = Math.abs(close - open) / (high - low) * height;
  const bodyY = y + (Math.min(close, open) - low) / (high - low) * height;
  
  return (
    <g>
      {/* Wick */}
      <line
        x1={x + width / 2}
        y1={y}
        x2={x + width / 2}
        y2={y + height}
        stroke={color}
        strokeWidth={1}
      />
      {/* Body */}
      <rect
        x={x + width * 0.2}
        y={bodyY}
        width={width * 0.6}
        height={bodyHeight}
        fill={isGreen ? color : 'none'}
        stroke={color}
        strokeWidth={1}
      />
    </g>
  );
};

export const TradingChart: React.FC<TradingChartProps> = ({
  data,
  showIndicators = {},
  entryPoints = [],
  exitPoints = [],
  height = 500,
}) => {
  const chartData = useMemo(() => {
    return data.map((item, index) => ({
      ...item,
      timestamp: item.timestamp.getTime(),
      sma20: item.indicators.sma20,
      sma50: item.indicators.sma50,
      rsi: item.indicators.rsi,
      macd: item.indicators.macd,
      vwap: item.indicators.vwap,
    }));
  }, [data]);

  const formatXAxis = (tickItem: number) => {
    return format(new Date(tickItem), 'MMM dd');
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatXAxis}
            stroke="#9ca3af"
            fontSize={12}
          />
          <YAxis
            domain={['dataMin - 5', 'dataMax + 5']}
            stroke="#9ca3af"
            fontSize={12}
            tickFormatter={(value) => formatCurrency(value)}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Price Lines */}
          <Line
            type="monotone"
            dataKey="close"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Close Price"
          />

          {/* Technical Indicators */}
          {showIndicators.sma20 && (
            <Line
              type="monotone"
              dataKey="sma20"
              stroke="#f59e0b"
              strokeWidth={1.5}
              dot={false}
              name="SMA 20"
              strokeDasharray="5 5"
            />
          )}

          {showIndicators.sma50 && (
            <Line
              type="monotone"
              dataKey="sma50"
              stroke="#8b5cf6"
              strokeWidth={1.5}
              dot={false}
              name="SMA 50"
              strokeDasharray="5 5"
            />
          )}

          {showIndicators.vwap && (
            <Line
              type="monotone"
              dataKey="vwap"
              stroke="#06b6d4"
              strokeWidth={1.5}
              dot={false}
              name="VWAP"
              strokeDasharray="3 3"
            />
          )}

          {showIndicators.volume && (
            <Bar
              dataKey="volume"
              fill="#6b7280"
              opacity={0.3}
              yAxisId="volume"
              name="Volume"
            />
          )}

          {/* Entry Points */}
          {entryPoints.map((price, index) => (
            <ReferenceLine
              key={`entry-${index}`}
              y={price}
              stroke="#22c55e"
              strokeWidth={2}
              strokeDasharray="8 4"
              label={{ value: `Entry: ${formatCurrency(price)}`, position: 'topLeft' }}
            />
          ))}

          {/* Exit Points */}
          {exitPoints.map((price, index) => (
            <ReferenceLine
              key={`exit-${index}`}
              y={price}
              stroke="#ef4444"
              strokeWidth={2}
              strokeDasharray="8 4"
              label={{ value: `Exit: ${formatCurrency(price)}`, position: 'topRight' }}
            />
          ))}
        </ComposedChart>
      </ResponsiveContainer>

      {/* RSI Chart */}
      {showIndicators.rsi && (
        <div className="mt-4">
          <ResponsiveContainer width="100%" height={150}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="timestamp" tickFormatter={formatXAxis} stroke="#9ca3af" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={12} />
              <Tooltip
                formatter={(value: number) => [formatNumber(value), 'RSI']}
                labelFormatter={(label: number) => format(new Date(label), 'MMM dd, yyyy HH:mm')}
              />
              <Line
                type="monotone"
                dataKey="rsi"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
                name="RSI"
              />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" />
              <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="3 3" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* MACD Chart */}
      {showIndicators.macd && (
        <div className="mt-4">
          <ResponsiveContainer width="100%" height={150}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="timestamp" tickFormatter={formatXAxis} stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                formatter={(value: number, name: string) => [formatNumber(value), name]}
                labelFormatter={(label: number) => format(new Date(label), 'MMM dd, yyyy HH:mm')}
              />
              <Line
                type="monotone"
                dataKey="macd"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="MACD"
              />
              <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="3 3" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
