import React, { useState, useCallback, useEffect } from 'react';
import { Search, TrendingUp, DollarSign, Zap, Wheat } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { assetService } from '@/services/api';
import { debounce } from '@/lib/utils';
import type { Asset } from '@/types';

interface AssetSearchProps {
  onAssetSelect: (asset: Asset) => void;
  selectedAsset?: Asset;
}

const getAssetIcon = (type: Asset['type']) => {
  switch (type) {
    case 'stock':
      return <TrendingUp className="h-4 w-4" />;
    case 'crypto':
      return <DollarSign className="h-4 w-4" />;
    case 'future':
      return <Wheat className="h-4 w-4" />;
    case 'option':
      return <Zap className="h-4 w-4" />;
    default:
      return <TrendingUp className="h-4 w-4" />;
  }
};

const getAssetTypeColor = (type: Asset['type']) => {
  switch (type) {
    case 'stock':
      return 'text-blue-600 bg-blue-50';
    case 'crypto':
      return 'text-orange-600 bg-orange-50';
    case 'future':
      return 'text-green-600 bg-green-50';
    case 'option':
      return 'text-purple-600 bg-purple-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
};

export const AssetSearch: React.FC<AssetSearchProps> = ({ onAssetSelect, selectedAsset }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const debouncedSearch = useCallback(
    debounce(async (query: string) => {
      if (query.trim().length < 2) {
        setSearchResults([]);
        setShowResults(false);
        return;
      }

      setIsLoading(true);
      try {
        const results = await assetService.searchAssets(query);
        setSearchResults(results);
        setShowResults(true);
      } catch (error) {
        console.error('Search error:', error);
        setSearchResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    []
  );

  useEffect(() => {
    debouncedSearch(searchQuery);
  }, [searchQuery, debouncedSearch]);

  const handleAssetSelect = (asset: Asset) => {
    onAssetSelect(asset);
    setShowResults(false);
    setSearchQuery('');
  };

  const popularAssets: Asset[] = [
    { symbol: 'AAPL', name: 'Apple Inc.', type: 'stock', exchange: 'NASDAQ' },
    { symbol: 'TSLA', name: 'Tesla Inc.', type: 'stock', exchange: 'NASDAQ' },
    { symbol: 'BTC-USD', name: 'Bitcoin', type: 'crypto' },
    { symbol: 'ETH-USD', name: 'Ethereum', type: 'crypto' },
    { symbol: 'GC=F', name: 'Gold Futures', type: 'future' },
    { symbol: 'CL=F', name: 'Crude Oil Futures', type: 'future' },
  ];

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search stocks, crypto, futures..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
        
        {showResults && (
          <Card className="absolute top-full left-0 right-0 z-50 mt-1 max-h-80 overflow-y-auto">
            <CardContent className="p-0">
              {isLoading ? (
                <div className="p-4 text-center text-muted-foreground">
                  Searching...
                </div>
              ) : searchResults.length > 0 ? (
                <div className="divide-y">
                  {searchResults.map((asset) => (
                    <button
                      key={asset.symbol}
                      onClick={() => handleAssetSelect(asset)}
                      className="w-full p-3 text-left hover:bg-accent transition-colors flex items-center gap-3"
                    >
                      <div className={`p-1.5 rounded ${getAssetTypeColor(asset.type)}`}>
                        {getAssetIcon(asset.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium">{asset.symbol}</div>
                        <div className="text-sm text-muted-foreground truncate">
                          {asset.name}
                        </div>
                        {asset.exchange && (
                          <div className="text-xs text-muted-foreground">
                            {asset.exchange}
                          </div>
                        )}
                      </div>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${getAssetTypeColor(asset.type)}`}>
                        {asset.type.toUpperCase()}
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="p-4 text-center text-muted-foreground">
                  No assets found
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {selectedAsset && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded ${getAssetTypeColor(selectedAsset.type)}`}>
                {getAssetIcon(selectedAsset.type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold">{selectedAsset.symbol}</div>
                <div className="text-sm text-muted-foreground truncate">
                  {selectedAsset.name}
                </div>
                {selectedAsset.exchange && (
                  <div className="text-xs text-muted-foreground">
                    {selectedAsset.exchange}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div>
        <h3 className="font-medium mb-3">Popular Assets</h3>
        <div className="space-y-2">
          {popularAssets.map((asset) => (
            <Button
              key={asset.symbol}
              variant="ghost"
              onClick={() => handleAssetSelect(asset)}
              className="w-full justify-start h-auto p-3"
            >
              <div className={`p-1.5 rounded mr-3 ${getAssetTypeColor(asset.type)}`}>
                {getAssetIcon(asset.type)}
              </div>
              <div className="flex-1 text-left">
                <div className="font-medium">{asset.symbol}</div>
                <div className="text-sm text-muted-foreground">
                  {asset.name}
                </div>
              </div>
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
};
