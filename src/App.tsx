import React, { useState, useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AssetSearch } from '@/components/sidebar/AssetSearch';
import { StrategySelector } from '@/components/strategy/StrategySelector';
import { ForecastResult } from '@/components/strategy/ForecastResult';
import { TradingChart } from '@/components/charts/TradingChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar,
  Settings,
  Play,
  Download
} from 'lucide-react';
import type { Asset, Strategy, ForecastResult as ForecastType, ChartData, TimeFrame } from '@/types';
import { priceService, forecastService, exportService } from '@/services/api';
import { formatCurrency, formatPercent } from '@/lib/utils';

const queryClient = new QueryClient();

const Badge = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
    {children}
  </span>
);

function TradingApp() {
  const [selectedAsset, setSelectedAsset] = useState<Asset>();
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy>();
  const [selectedTimeframe, setSelectedTimeframe] = useState<TimeFrame>('1d');
  const [forecast, setForecast] = useState<ForecastType>();
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [isLoadingForecast, setIsLoadingForecast] = useState(false);
  const [isLoadingChart, setIsLoadingChart] = useState(false);
  const [showIndicators, setShowIndicators] = useState({
    sma20: true,
    sma50: true,
    rsi: false,
    macd: false,
    volume: false,
    vwap: true,
  });

  const timeframes: TimeFrame[] = ['1h', '4h', '1d', '1w', '1M', '3M', '6M', '1Y', '3Y', '5Y', 'YTD'];

  const handleAssetSelect = useCallback(async (asset: Asset) => {
    setSelectedAsset(asset);
    setForecast(undefined);
    
    // Load chart data
    setIsLoadingChart(true);
    try {
      const priceData = await priceService.getHistoricalData(asset.symbol, selectedTimeframe);
      // Transform price data to chart data with indicators
      const chartData: ChartData[] = priceData.map((price, index) => ({
        ...price,
        indicators: {
          sma20: index >= 19 ? priceData.slice(index - 19, index + 1).reduce((sum, p) => sum + p.close, 0) / 20 : undefined,
          sma50: index >= 49 ? priceData.slice(index - 49, index + 1).reduce((sum, p) => sum + p.close, 0) / 50 : undefined,
          rsi: 50, // Placeholder - would be calculated with actual RSI logic
          macd: 0, // Placeholder
          vwap: price.vwap,
        }
      }));
      setChartData(chartData);
    } catch (error) {
      console.error('Failed to load chart data:', error);
    } finally {
      setIsLoadingChart(false);
    }
  }, [selectedTimeframe]);

  const handleStrategySelect = useCallback((strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setForecast(undefined);
  }, []);

  const handleGenerateForecast = useCallback(async () => {
    if (!selectedAsset || !selectedStrategy) return;

    setIsLoadingForecast(true);
    try {
      const forecastResult = await forecastService.generateForecast(
        selectedAsset.symbol,
        selectedStrategy.id,
        selectedTimeframe
      );
      setForecast(forecastResult);
    } catch (error) {
      console.error('Failed to generate forecast:', error);
    } finally {
      setIsLoadingForecast(false);
    }
  }, [selectedAsset, selectedStrategy, selectedTimeframe]);

  const handleExport = useCallback(async (type: 'pdf' | 'csv') => {
    if (!forecast) return;
    
    try {
      const blob = await exportService.exportToPDF(forecast, 'forecast');
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `forecast-${selectedAsset?.symbol}-${Date.now()}.${type}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
  }, [forecast, selectedAsset]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">Trading Research Platform</h1>
                <p className="text-sm text-muted-foreground">Multi-Asset Strategy Research & Forecasting</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6 h-[calc(100vh-8rem)]">
          {/* Left Sidebar */}
          <div className="col-span-3 space-y-6 overflow-y-auto">
            <AssetSearch
              onAssetSelect={handleAssetSelect}
              selectedAsset={selectedAsset}
            />
            
            <StrategySelector
              selectedAsset={selectedAsset}
              onStrategySelect={handleStrategySelect}
              selectedStrategy={selectedStrategy}
            />

            {/* News Section Placeholder */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Market News</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  News feed will be implemented here
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="col-span-9 space-y-6">
            {/* Timeframe and Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span className="text-sm font-medium">Timeframe:</span>
                <div className="flex gap-1">
                  {timeframes.map(tf => (
                    <Button
                      key={tf}
                      variant={selectedTimeframe === tf ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedTimeframe(tf)}
                    >
                      {tf}
                    </Button>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleGenerateForecast}
                  disabled={!selectedAsset || !selectedStrategy || isLoadingForecast}
                  className="flex items-center gap-2"
                >
                  <Play className="h-4 w-4" />
                  {isLoadingForecast ? 'Generating...' : 'Generate Forecast'}
                </Button>
              </div>
            </div>

            {/* Chart Section */}
            <Card className="flex-1">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    {selectedAsset ? `${selectedAsset.symbol} - ${selectedAsset.name}` : 'Select an Asset'}
                  </CardTitle>
                  
                  {selectedAsset && (
                    <div className="flex items-center gap-4">
                      <div className="text-sm">
                        <span className="text-muted-foreground">Price: </span>
                        <span className="font-semibold">{formatCurrency(chartData[chartData.length - 1]?.close || 0)}</span>
                      </div>
                      <div className="flex gap-2">
                        {Object.entries(showIndicators).map(([key, value]) => (
                          <Button
                            key={key}
                            variant={value ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setShowIndicators(prev => ({ ...prev, [key]: !prev[key as keyof typeof prev] }))}
                          >
                            {key.toUpperCase()}
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {isLoadingChart ? (
                  <div className="h-96 flex items-center justify-center">
                    <p className="text-muted-foreground">Loading chart data...</p>
                  </div>
                ) : chartData.length > 0 ? (
                  <TradingChart
                    data={chartData}
                    showIndicators={showIndicators}
                    entryPoints={forecast?.entryPoints}
                    exitPoints={forecast?.exitPoints}
                    height={400}
                  />
                ) : (
                  <div className="h-96 flex items-center justify-center">
                    <p className="text-muted-foreground">Select an asset to view chart</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Forecast Results */}
            {forecast && (
              <ForecastResult
                forecast={forecast}
                onExport={handleExport}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TradingApp />
    </QueryClientProvider>
  );
}

export default App;
