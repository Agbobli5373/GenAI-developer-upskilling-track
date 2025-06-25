import React, { useState, useCallback, useEffect } from "react";
import {
  MagnifyingGlassIcon,
  SparklesIcon,
  DocumentTextIcon,
  ClockIcon,
  LightBulbIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { apiService } from "../services/api";
import {
  EnhancedRAGResponse,
  QueryOptimizationResponse,
  QuerySuggestion,
  QueryPerformanceAnalysis,
  IntelligentSearchResponse,
} from "../types";

interface EnhancedRAGSearchProps {
  onResults?: (results: any) => void;
}

export const EnhancedRAGSearch: React.FC<EnhancedRAGSearchProps> = ({
  onResults,
}) => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<EnhancedRAGResponse | null>(null);
  const [optimizedQuery, setOptimizedQuery] =
    useState<QueryOptimizationResponse | null>(null);
  const [suggestions, setSuggestions] = useState<QuerySuggestion[]>([]);
  const [performance, setPerformance] =
    useState<QueryPerformanceAnalysis | null>(null);
  const [activeTab, setActiveTab] = useState<
    "rag" | "optimization" | "suggestions" | "performance"
  >("rag");
  const [useOptimization, setUseOptimization] = useState(true);
  const [useIntelligentSearch, setUseIntelligentSearch] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get query suggestions as user types
  const fetchSuggestions = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 3) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await apiService.getQuerySuggestions(searchQuery);
      setSuggestions(response.suggestions || []);
    } catch (err) {
      console.error("Failed to fetch suggestions:", err);
    }
  }, []);

  // Debounced suggestions
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query) {
        fetchSuggestions(query);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, fetchSuggestions]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      let searchResults;

      if (useIntelligentSearch) {
        // Use intelligent search that combines everything
        const intelligentResponse = await apiService.intelligentSearch({
          query,
          use_optimization: useOptimization,
          max_results: 10,
        });
        searchResults = intelligentResponse.data;
        setResults(searchResults.rag_response);
        setOptimizedQuery(searchResults.optimization);
        setPerformance(searchResults.performance);
      } else {
        // Use enhanced RAG search
        const ragParams = useOptimization
          ? { query, optimize_query: true, max_results: 10 }
          : { query, max_results: 10 };

        const ragResponse = await apiService.enhancedRAGSearch(ragParams);
        searchResults = ragResponse.data;
        setResults(searchResults);

        // Optionally get query optimization separately
        if (useOptimization) {
          try {
            const optimization = await apiService.optimizeQuery({
              query,
              context: "legal document search",
            });
            setOptimizedQuery(optimization.data);
          } catch (err) {
            console.warn("Query optimization failed:", err);
          }
        }

        // Get performance analysis
        try {
          const perfAnalysis = await apiService.analyzeQueryPerformance({
            query,
          });
          setPerformance(perfAnalysis.data);
        } catch (err) {
          console.warn("Performance analysis failed:", err);
        }
      }

      if (onResults) {
        onResults(searchResults);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Search failed. Please try again."
      );
      console.error("Search error:", err);
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

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      {/* Search Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <SparklesIcon className="h-6 w-6 text-blue-600" />
          Enhanced Legal RAG Search
        </h2>
        <p className="text-gray-600">
          AI-powered legal document search with query optimization and
          intelligent analysis
        </p>
      </div>

      {/* Search Options */}
      <div className="flex flex-wrap gap-4 justify-center">
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={useOptimization}
            onChange={(e) => setUseOptimization(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Query Optimization</span>
        </label>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={useIntelligentSearch}
            onChange={(e) => setUseIntelligentSearch(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Intelligent Search</span>
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
            placeholder="Enter your legal question or search query..."
            className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={3}
          />
          <button
            onClick={handleSearch}
            disabled={isLoading || !query.trim()}
            className="absolute right-2 top-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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

      {/* Results Tabs */}
      {(results || optimizedQuery || performance) && (
        <div className="space-y-4">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab("rag")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "rag"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <DocumentTextIcon className="inline h-4 w-4 mr-1" />
                RAG Results
              </button>
              {optimizedQuery && (
                <button
                  onClick={() => setActiveTab("optimization")}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "optimization"
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <Cog6ToothIcon className="inline h-4 w-4 mr-1" />
                  Query Optimization
                </button>
              )}
              {performance && (
                <button
                  onClick={() => setActiveTab("performance")}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "performance"
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <ChartBarIcon className="inline h-4 w-4 mr-1" />
                  Performance
                </button>
              )}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="space-y-6">
            {activeTab === "rag" && results && (
              <div className="space-y-6">
                {/* Answer */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-blue-900 mb-3">
                    AI-Generated Answer
                  </h3>
                  <div className="text-blue-800 whitespace-pre-wrap leading-relaxed">
                    {results.answer}
                  </div>
                  {results.confidence_score !== undefined && (
                    <div className="mt-3 text-sm text-blue-600">
                      Confidence: {Math.round(results.confidence_score * 100)}%
                    </div>
                  )}
                </div>

                {/* Legal Analysis */}
                {results.legal_analysis && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-yellow-900 mb-3">
                      Legal Analysis
                    </h3>
                    <div className="space-y-3">
                      {results.legal_analysis.key_legal_concepts && (
                        <div>
                          <h4 className="font-medium text-yellow-800">
                            Key Legal Concepts:
                          </h4>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {results.legal_analysis.key_legal_concepts.map(
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
                      {results.legal_analysis.jurisdictions &&
                        results.legal_analysis.jurisdictions.length > 0 && (
                          <div>
                            <h4 className="font-medium text-yellow-800">
                              Jurisdictions:
                            </h4>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {results.legal_analysis.jurisdictions.map(
                                (jurisdiction, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-1 bg-yellow-200 text-yellow-800 rounded-md text-sm"
                                  >
                                    {jurisdiction}
                                  </span>
                                )
                              )}
                            </div>
                          </div>
                        )}
                      {results.legal_analysis.risk_factors &&
                        results.legal_analysis.risk_factors.length > 0 && (
                          <div>
                            <h4 className="font-medium text-yellow-800">
                              Risk Factors:
                            </h4>
                            <ul className="list-disc list-inside mt-1 text-yellow-700">
                              {results.legal_analysis.risk_factors.map(
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
                {results.sources && results.sources.length > 0 && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Source Documents ({results.sources.length})
                    </h3>
                    <div className="grid gap-4 md:grid-cols-2">
                      {results.sources.map((source, index) => (
                        <div
                          key={index}
                          className="bg-white border border-gray-200 rounded-lg p-4"
                        >
                          <h4 className="font-medium text-gray-900 mb-2">
                            {source.title}
                          </h4>
                          <p className="text-sm text-gray-600 mb-2 line-clamp-3">
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

                {/* Cross References */}
                {results.cross_references &&
                  results.cross_references.length > 0 && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-green-900 mb-4">
                        Related Legal References
                      </h3>
                      <div className="space-y-3">
                        {results.cross_references.map((ref, index) => (
                          <div key={index} className="flex items-start gap-3">
                            <div className="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                            <div>
                              <div className="font-medium text-green-900">
                                {ref.title}
                              </div>
                              <div className="text-sm text-green-700">
                                {ref.description}
                              </div>
                              <div className="text-xs text-green-600">
                                Relationship: {ref.relationship_type} |
                                Relevance:{" "}
                                {Math.round(ref.relevance_score * 100)}%
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
              </div>
            )}

            {activeTab === "optimization" && optimizedQuery && (
              <div className="space-y-4">
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-purple-900 mb-3">
                    Optimized Query
                  </h3>
                  <div className="bg-white border border-purple-200 rounded p-3 mb-4">
                    <div className="text-purple-800 font-mono">
                      {optimizedQuery.optimized_query}
                    </div>
                  </div>
                  {optimizedQuery.explanation && (
                    <div>
                      <h4 className="font-medium text-purple-800 mb-2">
                        Optimization Explanation:
                      </h4>
                      <div className="text-purple-700">
                        {optimizedQuery.explanation}
                      </div>
                    </div>
                  )}
                  {optimizedQuery.suggested_refinements &&
                    optimizedQuery.suggested_refinements.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium text-purple-800 mb-2">
                          Suggested Refinements:
                        </h4>
                        <ul className="list-disc list-inside text-purple-700">
                          {optimizedQuery.suggested_refinements.map(
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

            {activeTab === "performance" && performance && (
              <div className="space-y-4">
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-indigo-900 mb-4">
                    Query Performance Analysis
                  </h3>

                  {/* Performance Metrics */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-indigo-900">
                        {Math.round(performance.complexity_score * 100)}%
                      </div>
                      <div className="text-sm text-indigo-600">Complexity</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-indigo-900">
                        {Math.round(performance.clarity_score * 100)}%
                      </div>
                      <div className="text-sm text-indigo-600">Clarity</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-indigo-900">
                        {Math.round(performance.specificity_score * 100)}%
                      </div>
                      <div className="text-sm text-indigo-600">Specificity</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-indigo-900">
                        {Math.round(performance.overall_score * 100)}%
                      </div>
                      <div className="text-sm text-indigo-600">Overall</div>
                    </div>
                  </div>

                  {/* Identified Issues */}
                  {performance.identified_issues &&
                    performance.identified_issues.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-medium text-indigo-800 mb-2">
                          Identified Issues:
                        </h4>
                        <ul className="list-disc list-inside text-indigo-700">
                          {performance.identified_issues.map((issue, idx) => (
                            <li key={idx}>{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {/* Improvement Suggestions */}
                  {performance.improvement_suggestions &&
                    performance.improvement_suggestions.length > 0 && (
                      <div>
                        <h4 className="font-medium text-indigo-800 mb-2">
                          Improvement Suggestions:
                        </h4>
                        <ul className="list-disc list-inside text-indigo-700">
                          {performance.improvement_suggestions.map(
                            (suggestion, idx) => (
                              <li key={idx}>{suggestion}</li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedRAGSearch;
