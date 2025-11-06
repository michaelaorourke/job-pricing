'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import { Upload, FileText, TrendingUp, DollarSign, MapPin, Briefcase } from 'lucide-react';
import axios from 'axios';

const SalaryChatWidget = dynamic(() => import('@/components/SalaryChatWidget'), {
  ssr: false
});

const BenchmarkDetails = dynamic(() => import('@/components/BenchmarkDetails'), {
  ssr: false
});

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface JobAnalysis {
  id: string;
  job_title: string;
  location: string;
  detected_level: number;
  years_experience_min: number;
  years_experience_max: number;
  skills_extracted: string[];
  confidence_score: number;
}

interface SalaryRange {
  recommended_min: string;
  recommended_target: string;
  recommended_max: string;
  confidence_score: string;
  geographic_factor: string;
  market_insights: {
    market_position: string;
    retention_risk: string;
    competitive_analysis: {
      market_demand: string;
      recommendation: string;
    };
  };
}

function HomeContent() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get('job');

  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(null);
  const [salaryRange, setSalaryRange] = useState<SalaryRange | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    if (jobId) {
      loadJobData(jobId);
    }
  }, [jobId]);

  const loadJobData = async (id: string) => {
    try {
      const [jobResponse, salaryResponse] = await Promise.all([
        axios.get(`${API_URL}/api/jobs/${id}`),
        axios.post(`${API_URL}/api/analysis/calculate/${id}`)
      ]);
      setJobAnalysis(jobResponse.data);
      setSalaryRange(salaryResponse.data);
    } catch (error) {
      console.error('Error loading job data:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    try {
      const response = await axios.post(`${API_URL}/api/jobs/upload`, formData);
      window.location.href = `/?job=${response.data.id}`;
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload file. Please try again.');
    }
    setIsUploading(false);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Salary Intelligence Platform
          </h1>
          <p className="text-xl text-gray-600">
            AI-powered job analysis and compensation benchmarking
          </p>
        </div>

        {/* Main Content */}
        {!jobAnalysis ? (
          // Upload Section
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="text-center">
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Upload className="w-10 h-10 text-blue-600" />
                </div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Upload Job Description
                </h2>
                <p className="text-gray-600 mb-8">
                  Upload a PDF, DOCX, or text file to get instant salary insights
                </p>

                <label className="block">
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    accept=".pdf,.docx,.txt"
                    className="hidden"
                    disabled={isUploading}
                  />
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 hover:border-blue-400 hover:bg-blue-50 transition-colors cursor-pointer">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <span className="text-gray-600">
                      {isUploading ? 'Analyzing...' : 'Click to upload or drag and drop'}
                    </span>
                    <p className="text-sm text-gray-500 mt-2">
                      Supports PDF, DOCX, and TXT files
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Market Analysis</h3>
                <p className="text-sm text-gray-600">
                  Real-time benchmarking against market data
                </p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <DollarSign className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Accurate Pricing</h3>
                <p className="text-sm text-gray-600">
                  AI-powered salary recommendations
                </p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <MapPin className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Geographic Insights</h3>
                <p className="text-sm text-gray-600">
                  Location-based compensation adjustments
                </p>
              </div>
            </div>
          </div>
        ) : (
          // Results Section with Benchmark Details
          <div className="max-w-7xl mx-auto">
            {/* Main Results Section */}
            <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
              {/* Job Header */}
              <div className="border-b border-gray-200 pb-6 mb-6">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  {jobAnalysis.job_title}
                </h2>
                <div className="flex items-center gap-4 text-gray-600">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {jobAnalysis.location}
                  </span>
                  <span className="flex items-center gap-1">
                    <Briefcase className="w-4 h-4" />
                    Level {jobAnalysis.detected_level}
                  </span>
                  <span>
                    {jobAnalysis.years_experience_min}-{jobAnalysis.years_experience_max} years exp.
                  </span>
                </div>
              </div>

              {/* Salary Range */}
              {salaryRange && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-gray-50 rounded-lg p-6">
                    <p className="text-sm text-gray-600 mb-2">Minimum</p>
                    <p className="text-2xl font-bold text-gray-900">
                      ${parseInt(salaryRange.recommended_min).toLocaleString()}
                    </p>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-6 border-2 border-blue-200">
                    <p className="text-sm text-blue-600 mb-2">Target</p>
                    <p className="text-3xl font-bold text-blue-600">
                      ${parseInt(salaryRange.recommended_target).toLocaleString()}
                    </p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-6">
                    <p className="text-sm text-gray-600 mb-2">Maximum</p>
                    <p className="text-2xl font-bold text-gray-900">
                      ${parseInt(salaryRange.recommended_max).toLocaleString()}
                    </p>
                  </div>
                </div>
              )}

              {/* Market Insights */}
              {salaryRange?.market_insights && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Market Analysis</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Position</span>
                        <span className="font-medium">{salaryRange.market_insights.market_position}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Retention Risk</span>
                        <span className="font-medium">{salaryRange.market_insights.retention_risk}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Geographic Factor</span>
                        <span className="font-medium">{salaryRange.geographic_factor}x</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Key Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {jobAnalysis.skills_extracted.map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Confidence Score */}
              {salaryRange && (
                <div className="mt-8 pt-6 border-t border-gray-200">
                  <div className="text-center text-sm text-gray-500">
                    Confidence Score: {(parseFloat(salaryRange.confidence_score) * 100).toFixed(0)}%
                  </div>
                </div>
              )}
            </div>

            {/* Benchmark Details Section - Now Below Main Results */}
            <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Data Analysis Details</h3>
              <BenchmarkDetails jobId={jobAnalysis.id} />
            </div>

            {/* Actions */}
            <div className="text-center">
              <button
                onClick={() => window.location.href = '/'}
                className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Analyze Another Job
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Chat Widget */}
      <SalaryChatWidget jobAnalysisId={jobAnalysis?.id} />
    </main>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HomeContent />
    </Suspense>
  );
}
