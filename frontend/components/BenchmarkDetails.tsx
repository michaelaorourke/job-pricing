'use client';

import React, { useEffect, useState } from 'react';
import {
  ChevronRight, Database, TrendingUp, Calculator,
  DollarSign, MapPin, Briefcase, BarChart3
} from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005';

interface BenchmarkDetailsProps {
  jobId: string;
}

interface BenchmarkData {
  job_analysis: {
    position: string;
    level: number;
    level_name: string;
    zone: number;
    zone_name: string;
    location: string;
    experience_range: string;
    skills: string[];
  };
  benchmark_data: {
    mercer: {
      count: number;
      p50_range: {
        min: number;
        max: number;
        avg: number;
      };
      p25_avg: number;
      p75_avg: number;
      data_points: Array<{
        job_title: string;
        location: string;
        p25: number;
        p50: number;
        p75: number;
        data_date: string;
      }>;
    };
    lattice: {
      count: number;
      p50_range: {
        min: number;
        max: number;
        avg: number;
      };
      p25_avg: number;
      p75_avg: number;
      data_points: Array<{
        job_title: string;
        location: string;
        p25: number;
        p50: number;
        p75: number;
        data_date: string;
      }>;
    };
  };
  calculation_breakdown: {
    base_p50: {
      mercer_avg: number;
      lattice_avg: number;
      combined_avg: number;
    };
    adjustments: {
      geographic_factor: number;
      geographic_adjustment: string;
      skills_premium: number;
      market_adjustment: number;
    };
    final_calculation: {
      base: number;
      final_target: number;
    };
  };
  salary_range: {
    minimum: number;
    target: number;
    maximum: number;
    confidence_score: number;
  };
}

export const BenchmarkDetails: React.FC<BenchmarkDetailsProps> = ({ jobId }) => {
  const [data, setData] = useState<BenchmarkData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSections, setExpandedSections] = useState({
    benchmarkData: true,
    calculation: true
  });

  useEffect(() => {
    if (jobId) {
      fetchBenchmarkDetails();
    }
  }, [jobId]);

  const fetchBenchmarkDetails = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/benchmarks/details/${jobId}`);
      setData(response.data);
    } catch (error) {
      console.error('Error fetching benchmark details:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Benchmark Data and Calculation Side by Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Benchmark Data Card */}
        <div className="bg-white rounded-lg shadow-sm">
          <div
            className="p-4 border-b border-gray-200 flex items-center justify-between cursor-pointer hover:bg-gray-50"
            onClick={() => toggleSection('benchmarkData')}
          >
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <Database className="w-5 h-5 text-green-600" />
              Benchmark Data Used
            </h3>
            <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${
              expandedSections.benchmarkData ? 'rotate-90' : ''
            }`} />
          </div>

          {expandedSections.benchmarkData && (
            <div className="p-4">
              {/* Mercer Data */}
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-600"></div>
                  Mercer ({data.benchmark_data.mercer.count} matches)
                </h4>
                <div className="bg-blue-50 rounded-lg p-3 mb-3">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">P50 Range:</span>
                      <span className="font-semibold">
                        {formatCurrency(data.benchmark_data.mercer.p50_range.min)} - {formatCurrency(data.benchmark_data.mercer.p50_range.max)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Average P50:</span>
                      <span className="font-semibold text-blue-600">
                        {formatCurrency(data.benchmark_data.mercer.p50_range.avg)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">P25/P75 Avg:</span>
                      <span className="font-semibold">
                        {formatCurrency(data.benchmark_data.mercer.p25_avg)} / {formatCurrency(data.benchmark_data.mercer.p75_avg)}
                      </span>
                    </div>
                  </div>
                </div>

                {data.benchmark_data.mercer.data_points.length > 0 && (
                  <div className="text-sm">
                    <p className="text-gray-500 mb-2">Sample Data Points:</p>
                    <div className="space-y-1">
                      {data.benchmark_data.mercer.data_points.slice(0, 3).map((point, idx) => (
                        <div key={idx} className="flex justify-between text-xs bg-gray-50 p-2 rounded">
                          <span className="text-gray-600 truncate pr-2">{point.job_title || 'Software Engineer'}</span>
                          <span className="font-medium">{formatCurrency(point.p50)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Lattice Data */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-600"></div>
                  Lattice ({data.benchmark_data.lattice.count} matches)
                </h4>
                <div className="bg-green-50 rounded-lg p-3 mb-3">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">P50 Range:</span>
                      <span className="font-semibold">
                        {formatCurrency(data.benchmark_data.lattice.p50_range.min)} - {formatCurrency(data.benchmark_data.lattice.p50_range.max)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Average P50:</span>
                      <span className="font-semibold text-green-600">
                        {formatCurrency(data.benchmark_data.lattice.p50_range.avg)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">P25/P75 Avg:</span>
                      <span className="font-semibold">
                        {formatCurrency(data.benchmark_data.lattice.p25_avg)} / {formatCurrency(data.benchmark_data.lattice.p75_avg)}
                      </span>
                    </div>
                  </div>
                </div>

                {data.benchmark_data.lattice.data_points.length > 0 && (
                  <div className="text-sm">
                    <p className="text-gray-500 mb-2">Sample Data Points:</p>
                    <div className="space-y-1">
                      {data.benchmark_data.lattice.data_points.slice(0, 3).map((point, idx) => (
                        <div key={idx} className="flex justify-between text-xs bg-gray-50 p-2 rounded">
                          <span className="text-gray-600 truncate pr-2">{point.job_title}</span>
                          <span className="font-medium">{formatCurrency(point.p50)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Calculation Breakdown Card */}
        <div className="bg-white rounded-lg shadow-sm">
          <div
            className="p-4 border-b border-gray-200 flex items-center justify-between cursor-pointer hover:bg-gray-50"
            onClick={() => toggleSection('calculation')}
          >
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <Calculator className="w-5 h-5 text-purple-600" />
              Calculation Breakdown
            </h3>
            <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${
              expandedSections.calculation ? 'rotate-90' : ''
            }`} />
          </div>

          {expandedSections.calculation && (
            <div className="p-4">
              <div className="space-y-3">
                {/* Base Calculation */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <h5 className="font-medium text-gray-900 mb-2 text-sm">Base P50 Calculation</h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Mercer Avg:</span>
                      <span className="font-medium">
                        {formatCurrency(data.calculation_breakdown.base_p50.mercer_avg)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Lattice Avg:</span>
                      <span className="font-medium">
                        {formatCurrency(data.calculation_breakdown.base_p50.lattice_avg)}
                      </span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="text-gray-900 font-medium">Combined:</span>
                      <span className="font-semibold text-blue-600">
                        {formatCurrency(data.calculation_breakdown.base_p50.combined_avg)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Adjustments */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <h5 className="font-medium text-gray-900 mb-2 text-sm">Adjustments Applied</h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Geographic:</span>
                      <span className="font-medium">
                        ×{data.calculation_breakdown.adjustments.geographic_factor}
                      </span>
                    </div>
                    {data.calculation_breakdown.adjustments.skills_premium > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Skills:</span>
                        <span className="font-medium">
                          +{(data.calculation_breakdown.adjustments.skills_premium * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                    {data.calculation_breakdown.adjustments.market_adjustment > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Market:</span>
                        <span className="font-medium">
                          +{(data.calculation_breakdown.adjustments.market_adjustment * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Final Range */}
                <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-3">
                  <h5 className="font-medium text-gray-900 mb-2 text-sm">Final Salary Range</h5>
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div>
                      <p className="text-xs text-gray-600">Min</p>
                      <p className="text-sm font-bold text-gray-900">
                        {formatCurrency(data.salary_range.minimum)}
                      </p>
                    </div>
                    <div className="border-x border-gray-200">
                      <p className="text-xs text-gray-600">Target</p>
                      <p className="text-base font-bold text-green-600">
                        {formatCurrency(data.salary_range.target)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Max</p>
                      <p className="text-sm font-bold text-gray-900">
                        {formatCurrency(data.salary_range.maximum)}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 pt-2 border-t border-gray-200">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Confidence:</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500 transition-all"
                            style={{ width: `${data.salary_range.confidence_score * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-gray-900">
                          {(data.salary_range.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BenchmarkDetails;