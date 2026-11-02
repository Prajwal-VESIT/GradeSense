import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import {
  GitCompare,
  Award,
  CheckCircle,
  HelpCircle,
  AlertCircle,
  Layers,
  ArrowRight,
} from 'lucide-react';

import ChartCard from '../components/ChartCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import { fetchModelComparison, fetchModelMetadata, fetchErrorAnalysis } from '../services/api';

export default function ModelComparison() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [models, setModels] = useState([]);
  const [metadata, setMetadata] = useState({});
  const [errorAnalysis, setErrorAnalysis] = useState({});
  const [scenario, setScenario] = useState('early_performance'); // 'early_performance' | 'grade_assisted'

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [compRes, metaRes, errRes] = await Promise.all([
          fetchModelComparison(),
          fetchModelMetadata(),
          fetchErrorAnalysis(),
        ]);
        setModels(compRes);
        setMetadata(metaRes);
        setErrorAnalysis(errRes);
      } catch (err) {
        setError(err.message || 'Failed to load model comparison benchmarks');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading model benchmarks and evaluation results..." fullPage />;
  }

  if (error) {
    return <ErrorAlert message={error} retry={() => window.location.reload()} />;
  }

  const filteredModels = models.filter((m) => m.scenario === scenario);
  const scenarioMeta = metadata[scenario] || {};
  const bestModelName = scenarioMeta.best_model;

  // Chart data for comparing Test MAE vs CV MAE
  const chartData = filteredModels.map((m) => ({
    name: m.model.replace('Regressor', ''),
    'CV MAE': m.cv_mae,
    'Test MAE': m.test_mae,
    'Test RMSE': m.test_rmse,
    isBest: m.model === bestModelName,
  }));

  // Error by range for active scenario
  const rangeErrors = errorAnalysis[scenario]?.error_by_range || [];

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Quantitative Model Comparison</h1>
        <p className="text-sm text-slate-500 mt-1">
          Benchmarking 6 regression algorithms under identical 5-fold cross-validation and 80/20 test split.
        </p>
      </div>

      {/* Scenario Selector */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setScenario('early_performance')}
          className={`px-5 py-3 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${
            scenario === 'early_performance'
              ? 'border-amber-600 text-amber-700 bg-amber-50/40'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Scenario A: Early-Performance (No G1/G2)</span>
        </button>

        <button
          onClick={() => setScenario('grade_assisted')}
          className={`px-5 py-3 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${
            scenario === 'grade_assisted'
              ? 'border-emerald-600 text-emerald-700 bg-emerald-50/40'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <CheckCircle className="w-4 h-4" />
          <span>Scenario B: Grade-Assisted (With G1 & G2)</span>
        </button>
      </div>

      {/* Scenario Overview Callout */}
      <div
        className={`p-4 rounded-xl border text-xs leading-relaxed flex items-start gap-3 ${
          scenario === 'early_performance'
            ? 'bg-amber-50 border-amber-200 text-amber-900'
            : 'bg-emerald-50 border-emerald-200 text-emerald-900'
        }`}
      >
        <Award className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">
            Best Selected Model:{' '}
            <span className="underline">{bestModelName || 'RandomForest'}</span>
          </span>
          <p className="mt-1">
            {scenario === 'early_performance'
              ? 'Selected based on lowest 5-fold Cross-Validation MAE on training data (without seeing test split). Achieves Test MAE of 3.00 and R² of 0.307 on 79 held-out test records.'
              : 'Selected based on lowest 5-fold Cross-Validation MAE on training data. Achieves Test MAE of 1.21 and R² of 0.803, demonstrating strong predictive accuracy once period grades are known.'}
          </p>
        </div>
      </div>

      {/* Benchmark Metrics Table */}
      <div className="card space-y-4">
        <h2 className="text-base font-bold text-slate-900">Model Evaluation Metrics Table</h2>
        <div className="table-container border border-slate-200 rounded-lg overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-100 text-slate-700 border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3 font-semibold">Algorithm</th>
                <th className="py-2.5 px-3 font-semibold text-right">CV MAE (5-Fold)</th>
                <th className="py-2.5 px-3 font-semibold text-right">Test MAE</th>
                <th className="py-2.5 px-3 font-semibold text-right">Test MSE</th>
                <th className="py-2.5 px-3 font-semibold text-right">Test RMSE</th>
                <th className="py-2.5 px-3 font-semibold text-right">Test R&sup2;</th>
                <th className="py-2.5 px-3 font-semibold text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredModels.map((m, idx) => {
                const isSelected = m.model === bestModelName;
                return (
                  <tr
                    key={idx}
                    className={`hover:bg-slate-50 transition-colors ${
                      isSelected ? 'bg-primary-50/50 font-semibold' : ''
                    }`}
                  >
                    <td className="py-2.5 px-3 font-medium flex items-center gap-2">
                      {isSelected && <Award className="w-4 h-4 text-primary-600 flex-shrink-0" />}
                      <span>{m.model}</span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-slate-600">
                      {m.cv_mae?.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-slate-900">
                      {m.test_mae?.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-slate-600">
                      {m.test_mse?.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-slate-600">
                      {m.test_rmse?.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-slate-800">
                      {m.test_r2?.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      {isSelected ? (
                        <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                          Selected Model
                        </span>
                      ) : m.model === 'DummyRegressor' ? (
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px]">
                          Baseline
                        </span>
                      ) : (
                        <span className="text-slate-400 text-[10px]">Evaluated</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Chart: CV MAE vs Test MAE */}
      <ChartCard
        title={`Cross-Validation vs Test MAE (${scenario.replace('_', ' ').toUpperCase()})`}
        description="Comparing 5-fold cross-validation MAE against held-out test MAE."
      >
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(val) => [`${val?.toFixed(3)} grade points`, '']}
                contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '6px' }} />
              <Bar dataKey="CV MAE" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Test MAE" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Error Analysis by Grade Range Table */}
      {rangeErrors.length > 0 && (
        <div className="card space-y-3">
          <h2 className="text-base font-bold text-slate-900">
            Error Analysis Across Performance Tiers ({scenario.replace('_', ' ').toUpperCase()})
          </h2>
          <p className="text-xs text-slate-500">
            Evaluating mean absolute error and residuals across grade brackets on the 79 test cases.
          </p>

          <div className="table-container border border-slate-200 rounded-lg overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-100 text-slate-700 border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3 font-semibold">Grade Range</th>
                  <th className="py-2.5 px-3 font-semibold text-right">Test Count</th>
                  <th className="py-2.5 px-3 font-semibold text-right">Mean Absolute Error</th>
                  <th className="py-2.5 px-3 font-semibold text-right">Mean Residual (Actual - Pred)</th>
                  <th className="py-2.5 px-3 font-semibold">Diagnostic Insight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {rangeErrors.map((re, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{re.grade_range}</td>
                    <td className="py-2.5 px-3 text-right font-mono">{re.count}</td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-slate-900">
                      {re.mean_abs_error?.toFixed(3)}
                    </td>
                    <td
                      className={`py-2.5 px-3 text-right font-mono font-semibold ${
                        re.mean_residual < 0 ? 'text-amber-600' : 'text-blue-600'
                      }`}
                    >
                      {re.mean_residual > 0 ? `+${re.mean_residual.toFixed(3)}` : re.mean_residual?.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-slate-500">
                      {re.mean_residual < 0 ? 'Overpredicting (actual < predicted)' : 'Underpredicting (actual > predicted)'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Metric Definitions Guide */}
      <div className="card bg-slate-50 border border-slate-200 space-y-3">
        <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-primary-600" />
          <span>Evaluation Metrics Glossary (Scale: 0 to 20 Points)</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-600">
          <div>
            <span className="font-semibold text-slate-800">Mean Absolute Error (MAE):</span> Average absolute deviation
            between predicted and actual grade. A test MAE of 1.21 means predictions deviate by approximately 1.2 grade points.
          </div>
          <div>
            <span className="font-semibold text-slate-800">Root Mean Squared Error (RMSE):</span> Penalizes larger errors
            more heavily than MAE. Useful for detecting extreme outlier mispredictions.
          </div>
          <div>
            <span className="font-semibold text-slate-800">Mean Squared Error (MSE):</span> Average of squared errors;
            the primary optimization loss during gradient-based training.
          </div>
          <div>
            <span className="font-semibold text-slate-800">Coefficient of Determination (R&sup2;):</span> Proportion of
            variance in final grade explained by the features. R&sup2; = 0.803 indicates over 80% variance explained.
          </div>
        </div>
      </div>
    </div>
  );
}
