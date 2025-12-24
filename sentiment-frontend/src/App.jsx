import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Header from './components/Header';
import StatsDashboard from './components/StatsDashboard';
import AnalysisInput from './components/AnalysisInput';
import ResultsDisplay from './components/ResultsDisplay';
import HistoryList from './components/HistoryList';
import AnalyticsChart from './components/AnalyticsChart';
import BatchAnalysis from './components/BatchAnalysis';
import Toast from './components/Toast';

// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function App() {
  // State
  const [stats, setStats] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });
  const [toast, setToast] = useState(null);
  const [activeTab, setActiveTab] = useState('analyze');
  const [isConnected, setIsConnected] = useState(true);

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/stats`);
      setStats({
        total_predictions: response.data.total_predictions,
        sentiment_distribution: response.data.sentiment_distribution,
        avg_confidence: response.data.avg_confidence
      });
      setHistory(response.data.recent_predictions);
      setIsConnected(true);
    } catch (error) {
      console.error("Error fetching stats:", error);
      setIsConnected(false);
    }
  }, []);

  // Fetch analytics
  const fetchAnalytics = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/stats/analytics?days=7`);
      setAnalytics(response.data);
    } catch (error) {
      console.error("Error fetching analytics:", error);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    fetchStats();
    fetchAnalytics();
  }, [fetchStats, fetchAnalytics]);

  // Show toast notification
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Handle single analysis
  const handleAnalyze = async (text) => {
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/predictions`, { text });

      // Smooth transition delay
      await new Promise(resolve => setTimeout(resolve, 400));

      setResult(response.data);
      fetchStats();
      fetchAnalytics();

      showToast(`Analysis complete: ${response.data.sentiment.toUpperCase()}`, 'success');
    } catch (error) {
      console.error("Analysis failed:", error);
      showToast(
        error.response?.data?.detail || "Analysis failed. Ensure backend is running.",
        'error'
      );
    } finally {
      setLoading(false);
    }
  };

  // Handle batch analysis
  const handleBatchAnalyze = async (texts) => {
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/predictions/batch`, { texts });

      fetchStats();
      fetchAnalytics();

      showToast(`Batch complete: ${response.data.total_processed} texts analyzed`, 'success');
      return response.data;
    } catch (error) {
      console.error("Batch analysis failed:", error);
      showToast(
        error.response?.data?.detail || "Batch analysis failed.",
        'error'
      );
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Handle export
  const handleExport = async (format = 'json') => {
    try {
      const response = await axios.get(`${API_URL}/predictions/export`, {
        params: { format, limit: 1000 },
        responseType: format === 'csv' ? 'blob' : 'json'
      });

      if (format === 'csv') {
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sentiment_predictions.csv';
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sentiment_predictions.json';
        a.click();
        window.URL.revokeObjectURL(url);
      }

      showToast(`Exported ${format.toUpperCase()} successfully`, 'success');
    } catch (error) {
      console.error("Export failed:", error);
      showToast("Export failed", 'error');
    }
  };

  // Toggle theme
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <>
      {/* Animated Background */}
      <div className="animated-bg" />

      {/* Main App Container */}
      <div className="min-h-screen relative">
        {/* Header */}
        <Header
          theme={theme}
          onThemeToggle={toggleTheme}
          onExport={handleExport}
          isConnected={isConnected}
        />

        {/* Main Content */}
        <main className="container" style={{ paddingTop: '2rem', paddingBottom: '4rem' }}>
          {/* Page Title */}
          <div className="text-center" style={{ marginBottom: '3rem' }}>
            <h1 className="heading-1" style={{ marginBottom: '0.5rem' }}>
              SentimentAI
            </h1>
            <p className="text-body">
              Real-time sentiment analysis powered by machine learning
            </p>
          </div>

          {/* Stats Dashboard */}
          <StatsDashboard stats={stats} />

          {/* Tab Navigation */}
          <div className="flex justify-center gap-4" style={{ marginBottom: '2rem' }}>
            <button
              className={`btn ${activeTab === 'analyze' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('analyze')}
            >
              Single Analysis
            </button>
            <button
              className={`btn ${activeTab === 'batch' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('batch')}
            >
              Batch Analysis
            </button>
            <button
              className={`btn ${activeTab === 'analytics' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('analytics')}
            >
              Analytics
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'analyze' && (
            <div className="animate-fade-in">
              <AnalysisInput onAnalyze={handleAnalyze} loading={loading} />
              {result && <ResultsDisplay result={result} />}
              <HistoryList history={history} />
            </div>
          )}

          {activeTab === 'batch' && (
            <div className="animate-fade-in">
              <BatchAnalysis onAnalyze={handleBatchAnalyze} loading={loading} />
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="animate-fade-in">
              <AnalyticsChart analytics={analytics} />
            </div>
          )}
        </main>

        {/* Toast Notification */}
        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
          />
        )}
      </div>
    </>
  );
}

export default App;
