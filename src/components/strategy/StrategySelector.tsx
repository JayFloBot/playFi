import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { strategyService } from '@/services/api';
import type { Strategy, Asset } from '@/types';
import { TrendingUp, TrendingDown, BarChart3, Zap, Target, Shield } from 'lucide-react';

interface StrategySelectorProps {
  selectedAsset?: Asset;
  onStrategySelect: (strategy: Strategy) => void;
  selectedStrategy?: Strategy;
}

const getStrategyIcon = (category: Strategy['category']) => {
  switch (category) {
    case 'long':
      return <TrendingUp className="h-4 w-4" />;
    case 'short':
      return <TrendingDown className="h-4 w-4" />;
    case 'spread':
      return <BarChart3 className="h-4 w-4" />;
    case 'straddle':
    case 'strangle':
      return <Zap className="h-4 w-4" />;
    case 'iron_condor':
      return <Target className="h-4 w-4" />;
    default:
      return <Shield className="h-4 w-4" />;
  }
};

const getRiskColor = (risk: Strategy['riskLevel']) => {
  switch (risk) {
    case 'low':
      return 'bg-green-100 text-green-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'high':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const Badge = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
    {children}
  </span>
);

export const StrategySelector: React.FC<StrategySelectorProps> = ({
  selectedAsset,
  onStrategySelect,
  selectedStrategy,
}) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedType, setSelectedType] = useState<string>('all');

  useEffect(() => {
    const loadStrategies = async () => {
      setIsLoading(true);
      try {
        const assetType = selectedAsset?.type;
        const data = await strategyService.getStrategies(assetType);
        setStrategies(data);
      } catch (error) {
        console.error('Failed to load strategies:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadStrategies();
  }, [selectedAsset]);

  const filteredStrategies = strategies.filter(strategy => 
    selectedType === 'all' || strategy.type === selectedType
  );

  const strategyTypes = ['all', 'equity', 'options', 'futures', 'crypto'];

  if (!selectedAsset) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-muted-foreground">Select an asset to view available strategies</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5" />
          Trading Strategies
        </CardTitle>
        <div className="flex flex-wrap gap-2">
          {strategyTypes.map(type => (
            <Button
              key={type}
              variant={selectedType === type ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedType(type)}
            >
              {type === 'all' ? 'All' : type.charAt(0).toUpperCase() + type.slice(1)}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Loading strategies...</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredStrategies.map(strategy => (
              <div
                key={strategy.id}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  selectedStrategy?.id === strategy.id
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
                onClick={() => onStrategySelect(strategy)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded">
                      {getStrategyIcon(strategy.category)}
                    </div>
                    <div>
                      <h4 className="font-medium">{strategy.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {strategy.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-col gap-1 items-end">
                    <Badge className={getRiskColor(strategy.riskLevel)}>
                      {strategy.riskLevel.toUpperCase()}
                    </Badge>
                    <Badge className="bg-blue-100 text-blue-800">
                      {strategy.type.toUpperCase()}
                    </Badge>
                  </div>
                </div>
                
                <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Capital Required:</span>
                    <span className="ml-2 font-medium">
                      ${strategy.capitalRequired.toLocaleString()}
                    </span>
                  </div>
                  {strategy.maxLoss && (
                    <div>
                      <span className="text-muted-foreground">Max Loss:</span>
                      <span className="ml-2 font-medium text-red-600">
                        ${strategy.maxLoss.toLocaleString()}
                      </span>
                    </div>
                  )}
                  {strategy.maxProfit && (
                    <div>
                      <span className="text-muted-foreground">Max Profit:</span>
                      <span className="ml-2 font-medium text-green-600">
                        ${strategy.maxProfit.toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {filteredStrategies.length === 0 && (
              <div className="text-center py-8">
                <p className="text-muted-foreground">
                  No strategies available for the selected criteria
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
