import React, { useState, useEffect } from "react";
import {
  SparklesIcon,
  BoltIcon,
  AcademicCapIcon,
  ChartBarIcon,
  CogIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
  DocumentTextIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";
import { apiService } from "../services/api";
import {
  IntelligentSearchRequest,
  IntelligentSearchResponse,
  QuerySuggestion,
} from "../types";

interface IntelligentSearchInterfaceProps {
  onResults?: (results: IntelligentSearchResponse) => void;
}

type SearchStrategy = "balanced" | "comprehensive" | "fast";

const strategyConfig = {
  balanced: {
    name: "Balanced",
    description: "Optimal balance of speed and comprehensiveness",
    icon: ChartBarIcon,
    color: "blue",
    maxResults: 10,
    recommendedFor: "General legal research and document analysis",
  },
  comprehensive: {
    name: "Comprehensive",
    description: "Deep analysis with extensive cross-referencing",
    icon: AcademicCapIcon,
    color: "green",
    maxResults: 20,
    recommendedFor: "Complex legal cases requiring thorough analysis",
  },
  fast: {
    name: "Fast",
    description: "Quick results for immediate insights",
    icon: BoltIcon,
    color: "yellow",
    maxResults: 5,
    recommendedFor: "Quick fact-checking and initial research",
  },
};

export const IntelligentSearchInterface: React.FC<
  IntelligentSearchInterfaceProps
> = ({ onResults }) => {
  const [query, setQuery] = useState("");
  const [selectedStrategy, setSelectedStrategy] =
    useState<SearchStrategy>("balanced");
  const [useOptimization, setUseOptimization] = useState(true);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<IntelligentSearchResponse | null>(
    null
  );
  const [suggestions, setSuggestions] = useState<QuerySuggestion[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | null>(null);

  // Get query suggestions
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length < 3) {
        setSuggestions([]);
        return;
      }

      try {
        const response = await apiService.getQuerySuggestions(query);
        setSuggestions(response.data.suggestions || []);
      } catch (err) {
        console.error("Failed to fetch suggestions:", err);
      }
    };

    const timer = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(timer);
  }, [query]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    const startTime = Date.now();

    try {
      const request: IntelligentSearchRequest = {
        query,
        document_ids:
          selectedDocuments.length > 0 ? selectedDocuments : undefined,
        use_optimization: useOptimization,
        max_results: strategyConfig[selectedStrategy].maxResults,
        search_strategy: selectedStrategy,
      };

      const response = await apiService.intelligentSearch(request);
      const endTime = Date.now();

      setSearchTime(endTime - startTime);
      setResults(response.data);

      if (onResults) {
        onResults(response.data);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Intelligent search failed. Please try again."
      );
      console.error("Intelligent search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: QuerySuggestion) => {
    setQuery(suggestion.query);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const getStrategyColorClasses = (
    strategy: SearchStrategy,
    selected: boolean
  ) => {
    const config = strategyConfig[strategy];
    const baseClasses =
      "relative rounded-lg p-4 cursor-pointer transition-all duration-200 ";

    if (selected) {
      return (
        baseClasses +
        `bg-${config.color}-50 border-2 border-${config.color}-500 shadow-md`
      );
    }

    return (
      baseClasses +
      `bg-white border-2 border-gray-200 hover:border-${config.color}-300 hover:bg-${config.color}-25`
    );
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <SparklesIcon className="h-6 w-6 text-indigo-600" />
          Intelligent Search Interface
        </h2>
        <p className="text-gray-600">
          AI-powered legal document search with adaptive strategies and
          optimization
        </p>
      </div>

      {/* Search Strategy Selection */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Search Strategy</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(strategyConfig).map(([key, config]) => {
            const strategy = key as SearchStrategy;
            const IconComponent = config.icon;
            const isSelected = selectedStrategy === strategy;

            return (
              <div
                key={key}
                onClick={() => setSelectedStrategy(strategy)}
                className={getStrategyColorClasses(strategy, isSelected)}
              >
                <div className="flex items-start gap-3">
                  <IconComponent
                    className={`h-6 w-6 flex-shrink-0 ${
                      isSelected ? `text-${config.color}-600` : "text-gray-400"
                    }`}
                  />
                  <div className="flex-1">
                    <h4
                      className={`font-medium ${
                        isSelected
                          ? `text-${config.color}-900`
                          : "text-gray-900"
                      }`}
                    >
                      {config.name}
                    </h4>
                    <p
                      className={`text-sm mt-1 ${
                        isSelected
                          ? `text-${config.color}-700`
                          : "text-gray-600"
                      }`}
                    >
                      {config.description}
                    </p>
                    <div
                      className={`text-xs mt-2 ${
                        isSelected
                          ? `text-${config.color}-600`
                          : "text-gray-500"
                      }`}
                    >
                      <div>Max Results: {config.maxResults}</div>
                      <div className="mt-1">
                        Best for: {config.recommendedFor}
                      </div>
                    </div>
                  </div>
                </div>
                {isSelected && (
                  <div
                    className={`absolute top-2 right-2 w-4 h-4 bg-${config.color}-500 rounded-full flex items-center justify-center`}
                  >
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Search Options */}
      <div className="flex flex-wrap gap-4 justify-center">
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={useOptimization}
            onChange={(e) => setUseOptimization(e.target.checked)}
            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span className="text-sm text-gray-700">
            Enable Query Optimization
          </span>
        </label>
      </div>

      {/* Search Input */}
      <div className="relative">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your intelligent search query..."
            className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            rows={3}
          />
          <button
            onClick={handleSearch}
            disabled={isLoading || !query.trim()}
            className="absolute right-2 top-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Searching...
              </>
            ) : (
              <>
                <SparklesIcon className="h-4 w-4" />
                Search
              </>
            )}
          </button>
        </div>

        {/* Query Suggestions */}
        {suggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-start gap-2"
              >
                <LightBulbIcon className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">
                    {suggestion.query}
                  </div>
                  {suggestion.explanation && (
                    <div className="text-sm text-gray-600">
                      {suggestion.explanation}
                    </div>
                  )}
                  <div className="text-xs text-gray-500">
                    Confidence: {Math.round(suggestion.confidence * 100)}%
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-2">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="text-red-700">{error}</div>
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Search Summary */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <ChartBarIcon className="h-5 w-5 text-indigo-600" />
                Search Summary
              </h3>
              {searchTime && (
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <ClockIcon className="h-4 w-4" />
                  {searchTime}ms
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-900">
                  {strategyConfig[selectedStrategy].name}
                </div>
                <div className="text-sm text-indigo-600">Strategy Used</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-900">
                  {results.rag_response?.sources?.length || 0}
                </div>
                <div className="text-sm text-purple-600">Sources Found</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-900">
                  {results.rag_response?.confidence_score
                    ? Math.round(results.rag_response.confidence_score * 100)
                    : 0}
                  %
                </div>
                <div className="text-sm text-green-600">Confidence</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-900">
                  {results.performance?.overall_score
                    ? Math.round(results.performance.overall_score * 100)
                    : 0}
                  %
                </div>
                <div className="text-sm text-blue-600">Query Quality</div>
              </div>
            </div>
          </div>

          {/* RAG Response */}
          {results.rag_response && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <DocumentTextIcon className="h-5 w-5 text-gray-600" />
                AI Analysis
              </h3>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div className="text-blue-900 whitespace-pre-wrap leading-relaxed">
                  {results.rag_response.answer}
                </div>
                {results.rag_response.confidence_score !== undefined && (
                  <div className="mt-3 text-sm text-blue-600">
                    Confidence:{" "}
                    {Math.round(results.rag_response.confidence_score * 100)}%
                  </div>
                )}
              </div>

              {/* Legal Analysis */}
              {results.rag_response.legal_analysis && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                  <h4 className="font-medium text-yellow-900 mb-3">
                    Legal Analysis
                  </h4>
                  <div className="space-y-3">
                    {results.rag_response.legal_analysis.key_legal_concepts && (
                      <div>
                        <span className="font-medium text-yellow-800">
                          Key Concepts:{" "}
                        </span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {results.rag_response.legal_analysis.key_legal_concepts.map(
                            (concept, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-yellow-200 text-yellow-800 rounded-md text-sm"
                              >
                                {concept}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    )}
                    {results.rag_response.legal_analysis.risk_factors &&
                      results.rag_response.legal_analysis.risk_factors.length >
                        0 && (
                        <div>
                          <span className="font-medium text-yellow-800">
                            Risk Factors:
                          </span>
                          <ul className="list-disc list-inside mt-1 text-yellow-700">
                            {results.rag_response.legal_analysis.risk_factors.map(
                              (risk, idx) => (
                                <li key={idx}>{risk}</li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                  </div>
                </div>
              )}

              {/* Source Documents */}
              {results.rag_response.sources &&
                results.rag_response.sources.length > 0 && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-3">
                      Source Documents ({results.rag_response.sources.length})
                    </h4>
                    <div className="grid gap-3 md:grid-cols-2">
                      {results.rag_response.sources.map((source, index) => (
                        <div
                          key={index}
                          className="bg-white border border-gray-200 rounded-lg p-3"
                        >
                          <h5 className="font-medium text-gray-900 mb-2">
                            {source.title}
                          </h5>
                          <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                            {source.content}
                          </p>
                          <div className="flex justify-between items-center text-xs text-gray-500">
                            <span>
                              Relevance:{" "}
                              {Math.round(source.relevance_score * 100)}%
                            </span>
                            <span>Page {source.page_number}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
            </div>
          )}

          {/* Query Optimization Results */}
          {results.optimization && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <CogIcon className="h-5 w-5 text-gray-600" />
                Query Optimization
              </h3>

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="mb-3">
                  <span className="font-medium text-purple-800">
                    Optimized Query:
                  </span>
                  <div className="bg-white border border-purple-200 rounded p-3 mt-2 font-mono text-purple-900">
                    {results.optimization.optimized_query}
                  </div>
                </div>

                {results.optimization.explanation && (
                  <div className="mb-3">
                    <span className="font-medium text-purple-800">
                      Explanation:
                    </span>
                    <div className="text-purple-700 mt-1">
                      {results.optimization.explanation}
                    </div>
                  </div>
                )}

                {results.optimization.suggested_refinements &&
                  results.optimization.suggested_refinements.length > 0 && (
                    <div>
                      <span className="font-medium text-purple-800">
                        Suggested Refinements:
                      </span>
                      <ul className="list-disc list-inside text-purple-700 mt-1">
                        {results.optimization.suggested_refinements.map(
                          (refinement, idx) => (
                            <li key={idx}>{refinement}</li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default IntelligentSearchInterface;
