import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  Target, 
  Percent, 
  DollarSign, 
  AlertCircle,
  CheckCircle,
  Download,
  FileText
} from 'lucide-react';
import type { ForecastResult } from '@/types';
import { formatCurrency, formatPercent } from '@/lib/utils';

interface ForecastResultProps {
  forecast: ForecastResult;
  onExport?: (type: 'pdf' | 'csv') => void;
}

const Badge = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
    {children}
  </span>
);

export const ForecastResult: React.FC<ForecastResultProps> = ({ forecast, onExport }) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 70) return 'text-green-600 bg-green-50';
    if (confidence >= 50) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getReturnColor = (expectedReturn: number) => {
    return expectedReturn > 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Forecast Result
          </div>
          <div className="flex items-center gap-2">
            {forecast.isValid ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600" />
            )}
            <Badge className={forecast.isValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
              {forecast.isValid ? 'VALID' : 'INVALID'}
            </Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Strategy & Asset Info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium text-sm text-muted-foreground">Strategy</h4>
            <p className="font-semibold">{forecast.strategy.name}</p>
            <p className="text-sm text-muted-foreground">{forecast.asset.symbol}</p>
          </div>
          <div>
            <h4 className="font-medium text-sm text-muted-foreground">Asset</h4>
            <p className="font-semibold">{forecast.asset.name}</p>
            <p className="text-sm text-muted-foreground">{forecast.asset.type.toUpperCase()}</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Percent className="h-4 w-4 text-blue-600" />
                <span className="text-sm text-muted-foreground">Confidence</span>
              </div>
              <div className={`text-2xl font-bold ${getConfidenceColor(forecast.confidence).split(' ')[0]}`}>
                {forecast.confidence}%
              </div>
              <Badge className={getConfidenceColor(forecast.confidence)}>
                {forecast.confidence >= 70 ? 'HIGH' : forecast.confidence >= 50 ? 'MEDIUM' : 'LOW'}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-green-600" />
                <span className="text-sm text-muted-foreground">Expected Return</span>
              </div>
              <div className={`text-2xl font-bold ${getReturnColor(forecast.expectedReturn)}`}>
                {formatCurrency(forecast.expectedReturn)}
              </div>
              <Badge className={forecast.expectedReturn > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                {forecast.expectedReturn > 0 ? 'PROFIT' : 'LOSS'}
              </Badge>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-purple-600" />
                <span className="text-sm text-muted-foreground">Win Probability</span>
              </div>
              <div className="text-2xl font-bold">
                {formatPercent(forecast.winProbability)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-orange-600" />
                <span className="text-sm text-muted-foreground">Risk/Reward</span>
              </div>
              <div className="text-2xl font-bold">
                {forecast.rewardRiskRatio.toFixed(2)}:1
              </div>
              <Badge className={forecast.rewardRiskRatio > 2 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                {forecast.rewardRiskRatio > 2 ? 'GOOD' : 'FAIR'}
              </Badge>
            </CardContent>
          </Card>
        </div>

        {/* Entry Points */}
        {forecast.entryPoints.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Suggested Entry Points</h4>
            <div className="flex flex-wrap gap-2">
              {forecast.entryPoints.map((price, index) => (
                <Badge key={index} className="bg-blue-100 text-blue-800">
                  {formatCurrency(price)}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Exit Points */}
        {forecast.exitPoints && forecast.exitPoints.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Suggested Exit Points</h4>
            <div className="flex flex-wrap gap-2">
              {forecast.exitPoints.map((price, index) => (
                <Badge key={index} className="bg-green-100 text-green-800">
                  {formatCurrency(price)}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Reasoning */}
        <div>
          <h4 className="font-medium mb-2">Analysis</h4>
          <p className="text-sm text-muted-foreground bg-muted/50 p-3 rounded">
            {forecast.reasoning}
          </p>
        </div>

        {/* Technical Conditions */}
        {forecast.technicalConditions.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Technical Conditions Met</h4>
            <div className="space-y-1">
              {forecast.technicalConditions.map((condition, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-3 w-3 text-green-600" />
                  <span>{condition}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Export Buttons */}
        {onExport && (
          <div className="flex gap-2 pt-4 border-t">
            <Button
              onClick={() => onExport('pdf')}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <FileText className="h-4 w-4" />
              Export PDF
            </Button>
            <Button
              onClick={() => onExport('csv')}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export CSV
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
