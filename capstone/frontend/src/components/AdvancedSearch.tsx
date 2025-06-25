import React, { useState, useCallback, useEffect } from "react";
import {
  Search,
  Filter,
  BarChart3,
  FileText,
  ArrowRight,
  Clock,
} from "lucide-react";
import { apiService } from "../services/api";
import { SearchResult, Document } from "../types";

interface AdvancedSearchProps {
  documents: Document[];
  onResultSelect?: (result: SearchResult) => void;
}

interface SearchFilters {
  documentIds?: string[];
  chunkTypes?: string[];
  enableQueryExpansion: boolean;
  enableReranking: boolean;
  searchMode: "semantic" | "advanced" | "comparison";
}

interface ComparisonResult {
  comparison_type: string;
  document_count: number;
  similarities?: Array<{
    documents: string[];
    similarity_score: number;
    common_terms: string[];
  }>;
  differences?: Array<{
    document: string;
    unique_terms: string[];
    uniqueness_score: number;
  }>;
  coverage_analysis?: {
    total_documents: number;
    topic_distribution: Record<string, Record<string, number>>;
  };
}

export const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  documents,
  onResultSelect,
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [comparisonResults, setComparisonResults] =
    useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTime, setSearchTime] = useState<number>(0);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);

  const [filters, setFilters] = useState<SearchFilters>({
    enableQueryExpansion: true,
    enableReranking: true,
    searchMode: "advanced",
  });

  // Debounced suggestions
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.length > 2) {
        try {
          const response = await apiService.getSearchSuggestions(query);
          setSuggestions(response.suggestions || []);
        } catch (error) {
          console.error("Error fetching suggestions:", error);
        }
      } else {
        setSuggestions([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;

    setLoading(true);
    const startTime = Date.now();

    try {
      let response;

      if (filters.searchMode === "advanced") {
        response = await apiService.advancedSearch({
          query,
          document_ids: filters.documentIds,
          search_filters: {
            chunk_types: filters.chunkTypes,
          },
          limit: 10,
          enable_query_expansion: filters.enableQueryExpansion,
          enable_reranking: filters.enableReranking,
        });
      } else if (
        filters.searchMode === "comparison" &&
        selectedDocuments.length >= 2
      ) {
        const compResponse = await apiService.multiDocumentComparison({
          document_ids: selectedDocuments,
          comparison_type: "similarity",
          analysis_depth: "standard",
        });
        setComparisonResults(compResponse);
        setResults([]);
        setSearchTime(Date.now() - startTime);
        return;
      } else {
        // Fallback to regular semantic search
        response = await apiService.semanticSearch({
          query,
          document_ids: filters.documentIds,
          chunk_types: filters.chunkTypes,
          limit: 10,
          similarity_threshold: 0.7,
          include_hybrid: true,
        });
      }

      setResults(response.results || []);
      setComparisonResults(null);
      setSearchTime(Date.now() - startTime);
    } catch (error) {
      console.error("Search error:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [query, filters, selectedDocuments]);

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setSuggestions([]);
  };

  const handleDocumentToggle = (docId: string) => {
    setSelectedDocuments((prev) =>
      prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId]
    );
  };

  const renderSearchResults = () => {
    if (comparisonResults) {
      return (
        <div className="space-y-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">
              Multi-Document Comparison Results
            </h3>
            <p className="text-blue-700">
              Analyzed {comparisonResults.document_count} documents for{" "}
              {comparisonResults.comparison_type}
            </p>
          </div>

          {comparisonResults.similarities && (
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">
                Document Similarities
              </h4>
              {comparisonResults.similarities.map((sim, index) => (
                <div
                  key={index}
                  className="bg-green-50 p-3 rounded border-l-4 border-green-400"
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">
                      Similarity Score
                    </span>
                    <span className="text-green-600 font-bold">
                      {(sim.similarity_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    Common terms: {sim.common_terms.slice(0, 5).join(", ")}
                  </p>
                  <p className="text-xs text-gray-500">
                    Documents: {sim.documents.join(" & ")}
                  </p>
                </div>
              ))}
            </div>
          )}

          {comparisonResults.differences && (
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Unique Content</h4>
              {comparisonResults.differences.map((diff, index) => (
                <div
                  key={index}
                  className="bg-orange-50 p-3 rounded border-l-4 border-orange-400"
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">
                      Uniqueness Score
                    </span>
                    <span className="text-orange-600 font-bold">
                      {(diff.uniqueness_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    Unique terms: {diff.unique_terms.slice(0, 5).join(", ")}
                  </p>
                  <p className="text-xs text-gray-500">
                    Document: {diff.document}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {results.map((result, index) => (
          <div
            key={result.id || index}
            className="bg-white p-4 rounded-lg border hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onResultSelect?.(result)}
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-medium text-gray-900 truncate">
                {result.document_title || "Untitled Document"}
              </h3>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                {result.combined_score && (
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                    Score: {(result.combined_score * 100).toFixed(0)}%
                  </span>
                )}
                {result.source && (
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      result.source === "hybrid"
                        ? "bg-purple-100 text-purple-800"
                        : result.source === "vector"
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {result.source}
                  </span>
                )}
              </div>
            </div>

            <p className="text-gray-600 text-sm mb-3 line-clamp-3">
              {result.content}
            </p>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{result.chunk_type && `Type: ${result.chunk_type}`}</span>
              <ArrowRight className="w-4 h-4" />
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Advanced Legal Search
          </h2>
          <p className="text-gray-600">
            Enhanced semantic search with query expansion, reranking, and
            multi-document analysis
          </p>
        </div>

        {/* Search Mode Selector */}
        <div className="mb-4">
          <div className="flex space-x-2">
            <button
              onClick={() =>
                setFilters((prev) => ({ ...prev, searchMode: "advanced" }))
              }
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filters.searchMode === "advanced"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <Search className="w-4 h-4 inline mr-1" />
              Advanced Search
            </button>
            <button
              onClick={() =>
                setFilters((prev) => ({ ...prev, searchMode: "comparison" }))
              }
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filters.searchMode === "comparison"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <BarChart3 className="w-4 h-4 inline mr-1" />
              Compare Documents
            </button>
          </div>
        </div>

        {/* Document Selection for Comparison */}
        {filters.searchMode === "comparison" && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">
              Select Documents to Compare
            </h3>
            <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
              {documents.map((doc) => (
                <label
                  key={doc.id}
                  className="flex items-center space-x-2 text-sm"
                >
                  <input
                    type="checkbox"
                    checked={selectedDocuments.includes(doc.id)}
                    onChange={() => handleDocumentToggle(doc.id)}
                    className="rounded border-gray-300"
                  />
                  <span className="truncate">{doc.title}</span>
                </label>
              ))}
            </div>
            {selectedDocuments.length < 2 && (
              <p className="text-sm text-amber-600 mt-2">
                Select at least 2 documents for comparison
              </p>
            )}
          </div>
        )}

        {/* Search Input */}
        <div className="relative mb-4">
          <div className="flex">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder={
                filters.searchMode === "comparison"
                  ? "Enter analysis focus (optional)"
                  : "Enter your legal search query..."
              }
              className="flex-1 px-4 py-3 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-3 bg-gray-100 border-t border-b border-gray-300 hover:bg-gray-200"
            >
              <Filter className="w-5 h-5" />
            </button>
            <button
              onClick={handleSearch}
              disabled={
                loading ||
                (filters.searchMode === "comparison" &&
                  selectedDocuments.length < 2)
              }
              className="px-6 py-3 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
            </button>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-b-lg shadow-lg z-10">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg space-y-3">
            <h3 className="font-medium text-gray-900">Search Options</h3>

            <div className="grid grid-cols-2 gap-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.enableQueryExpansion}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      enableQueryExpansion: e.target.checked,
                    }))
                  }
                  className="rounded border-gray-300"
                />
                <span className="text-sm">Query Expansion</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.enableReranking}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      enableReranking: e.target.checked,
                    }))
                  }
                  className="rounded border-gray-300"
                />
                <span className="text-sm">Result Reranking</span>
              </label>
            </div>
          </div>
        )}

        {/* Search Stats */}
        {(results.length > 0 || comparisonResults) && (
          <div className="mb-4 flex items-center space-x-4 text-sm text-gray-600">
            <span className="flex items-center">
              <FileText className="w-4 h-4 mr-1" />
              {comparisonResults
                ? `${comparisonResults.document_count} documents compared`
                : `${results.length} results found`}
            </span>
            <span className="flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              {searchTime}ms
            </span>
          </div>
        )}

        {/* Results */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              <p className="text-gray-600">
                {filters.searchMode === "comparison"
                  ? "Analyzing documents..."
                  : "Searching..."}
              </p>
            </div>
          ) : (
            renderSearchResults()
          )}
        </div>
      </div>
    </div>
  );
};
