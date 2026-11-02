import React, { useState, useEffect } from 'react';
import {
  Users,
  Award,
  TrendingUp,
  Cpu,
  Layers,
  BookOpen,
  AlertCircle,
  CheckCircle,
  HelpCircle,
} from 'lucide-react';
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

import StatCard from '../components/StatCard';
import ChartCard from '../components/ChartCard';
import CorrelationHeatmap from '../components/CorrelationHeatmap';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import {
  fetchDatasetSummary,
  fetchGradeDistribution,
  fetchModelComparison,
  fetchCorrelations,
  fetchInsights,
} from '../services/api';

export default function Overview() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [summary, setSummary] = useState(null);
  const [gradeDist, setGradeDist] = useState(null);
  const [models, setModels] = useState([]);
  const [correlations, setCorrelations] = useState(null);
  const [insights, setInsights] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [sumRes, gradeRes, modRes, corrRes, insRes] = await Promise.all([
          fetchDatasetSummary(),
          fetchGradeDistribution(),
          fetchModelComparison(),
          fetchCorrelations(),
          fetchInsights(),
        ]);
        setSummary(sumRes);
        setGradeDist(gradeRes);
        setModels(modRes);
        setCorrelations(corrRes);
        setInsights(insRes);
      } catch (err) {
        setError(err.message || 'Failed to load overview data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading academic analytics dashboard..." fullPage />;
  }

  if (error) {
    return <ErrorAlert message={error} retry={() => window.location.reload()} />;
  }

  // Format grade histogram data for Recharts
  const histogramData = gradeDist?.bins
    ? Object.entries(gradeDist.bins).map(([grade, count]) => ({
        grade: `G3=${grade}`,
        students: count,
      }))
    : [];

  // Group best models by scenario
  const earlyModels = models.filter((m) => m.scenario === 'early_performance');
  const assistedModels = models.filter((m) => m.scenario === 'grade_assisted');

  const bestEarly = earlyModels.reduce(
    (min, m) => {
      const mae = m.test_mae !== undefined ? m.test_mae : m.test_MAE;
      const minMae = min ? (min.test_mae !== undefined ? min.test_mae : min.test_MAE) : Infinity;
      return (!min || (mae !== null && mae < minMae)) ? { ...m, test_mae: mae } : min;
    },
    null
  );
  if (bestEarly && bestEarly.test_mae === undefined) {
    bestEarly.test_mae = bestEarly.test_MAE;
  }
  const bestAssisted = assistedModels.reduce(
    (min, m) => {
      const mae = m.test_mae !== undefined ? m.test_mae : m.test_MAE;
      const minMae = min ? (min.test_mae !== undefined ? min.test_mae : min.test_MAE) : Infinity;
      return (!min || (mae !== null && mae < minMae)) ? { ...m, test_mae: mae } : min;
    },
    null
  );
  if (bestAssisted && bestAssisted.test_mae === undefined) {
    bestAssisted.test_mae = bestAssisted.test_MAE;
  }

  // Model comparison bar chart data
  const comparisonData = earlyModels.map((em) => {
    const am = assistedModels.find((m) => m.model === em.model) || {};
    const emMae = em.test_mae !== undefined ? em.test_mae : em.test_MAE;
    const amMae = am.test_mae !== undefined ? am.test_mae : am.test_MAE;
    return {
      model: em.model.replace('Regressor', ''),
      earlyMAE: emMae,
      assistedMAE: amMae,
    };
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Welcome Banner */}
      <div className="bg-gradient-to-r from-primary-900 via-primary-800 to-indigo-900 rounded-2xl p-6 text-white shadow-sm">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-xs font-medium backdrop-blur-sm mb-3">
            <BookOpen className="w-3.5 h-3.5 text-primary-200" />
            <span>VESIT SEM VII &bull; Data Science CA2 Mini Project</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
            GradeSense &mdash; Academic Analytics & Performance Prediction
          </h1>
          <p className="mt-2 text-primary-100 text-sm md:text-base leading-relaxed">
            Understand student academic dynamics, explore correlation structures, and benchmark
            supervised regression algorithms across Early-Performance and Grade-Assisted scenarios.
          </p>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Users}
          label="Total Student Cohort"
          value={summary?.n_rows || 395}
          subtitle="UCI Student Performance Dataset"
        />
        <StatCard
          icon={Award}
          label="Average Final Grade (G3)"
          value={gradeDist?.mean !== undefined ? `${Number(gradeDist.mean).toFixed(2)} / 20` : '10.42 / 20'}
          subtitle={`Median: ${gradeDist?.median !== undefined ? Number(gradeDist.median).toFixed(1) : '11.0'} \u2022 Std: ${gradeDist?.std !== undefined ? Number(gradeDist.std).toFixed(2) : '4.58'}`}
        />
        <StatCard
          icon={Cpu}
          label="Best Early Model (Scenario A)"
          value={bestEarly && (bestEarly.test_mae !== undefined || bestEarly.test_MAE) ? `${(bestEarly.test_mae !== undefined ? bestEarly.test_mae : bestEarly.test_MAE).toFixed(2)} MAE` : '3.00 MAE'}
          subtitle={`${bestEarly?.model || 'RandomForest'} without prior term grades`}
        />
        <StatCard
          icon={TrendingUp}
          label="Best Grade-Assisted (Scenario B)"
          value={bestAssisted && (bestAssisted.test_mae !== undefined || bestAssisted.test_MAE) ? `${(bestAssisted.test_mae !== undefined ? bestAssisted.test_mae : bestAssisted.test_MAE).toFixed(2)} MAE` : '1.21 MAE'}
          subtitle={`${bestAssisted?.model || 'RandomForest'} with G1 & G2 grades`}
        />
      </div>

      {/* Prediction Scenarios Comparison Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card border-l-4 border-l-amber-500 bg-amber-50/30">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-amber-100 text-amber-700">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-base">Scenario A: Early-Performance Prediction</h3>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                Forecasts final outcome (G3) using 30 demographic, social, family, and attendance proxies,{' '}
                <strong>strictly excluding period grades G1 and G2</strong>. Demonstrates forecasting ability
                before any midterm assessments occur.
              </p>
              <div className="mt-3 flex items-center gap-3 text-xs font-medium text-amber-800">
                <span className="px-2 py-0.5 rounded bg-amber-100">Features: 30</span>
                <span className="px-2 py-0.5 rounded bg-amber-100">Best Test MAE: ~3.00</span>
                <span className="px-2 py-0.5 rounded bg-amber-100">Target Leakage: Strictly Zero</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card border-l-4 border-l-emerald-500 bg-emerald-50/30">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-emerald-100 text-emerald-700">
              <CheckCircle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-base">Scenario B: Grade-Assisted Prediction</h3>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                Incorporates first-period (G1) and second-period (G2) formative evaluations alongside
                background attributes. Reflects mid-semester counseling conditions with known formative grades.
              </p>
              <div className="mt-3 flex items-center gap-3 text-xs font-medium text-emerald-800">
                <span className="px-2 py-0.5 rounded bg-emerald-100">Features: 32</span>
                <span className="px-2 py-0.5 rounded bg-emerald-100">Best Test MAE: ~1.21</span>
                <span className="px-2 py-0.5 rounded bg-emerald-100">R&sup2;: ~0.803</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Grade Distribution Histogram */}
        <ChartCard
          title="Final Grade (G3) Distribution"
          description="Distribution of 395 students across the 0–20 integer grading scale."
        >
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={histogramData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis
                  dataKey="grade"
                  tick={{ fontSize: 10 }}
                  interval={1}
                  angle={-45}
                  textAnchor="end"
                />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val) => [`${val} students`, 'Frequency']}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
                <Bar dataKey="students" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500 mt-2 bg-slate-50 p-2.5 rounded border border-slate-100">
            <strong>Interpretation:</strong> Grades center around a mean of 10.42 (passing threshold = 10).
            A noticeable spike at G3=0 (9.6% of cohort) accounts for students who missed examinations or dropped out.
          </p>
        </ChartCard>

        {/* Model Comparison Chart */}
        <ChartCard
          title="Model Comparison (Held-Out Test MAE)"
          description="Mean Absolute Error across 6 regression models for both deployment scenarios."
        >
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="model" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} domain={[0, 4]} />
                <Tooltip
                  formatter={(val, name) => [
                    `${val?.toFixed(3)} grade points`,
                    name === 'earlyMAE' ? 'Scenario A (Early)' : 'Scenario B (Grade-Assisted)',
                  ]}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
                <Legend
                  formatter={(value) =>
                    value === 'earlyMAE' ? 'Scenario A (Early)' : 'Scenario B (Grade-Assisted)'
                  }
                  wrapperStyle={{ fontSize: '12px', paddingTop: '6px' }}
                />
                <Bar dataKey="earlyMAE" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="assistedMAE" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500 mt-2 bg-slate-50 p-2.5 rounded border border-slate-100">
            <strong>Interpretation:</strong> Lower MAE represents better accuracy. RandomForest achieves the lowest
            error in both scenarios. Incorporating G1 and G2 reduces test error by more than 59%.
          </p>
        </ChartCard>
      </div>

      {/* Correlation Matrix Heatmap */}
      {correlations && correlations.features && (
        <ChartCard
          title="Numerical Feature Correlation Matrix"
          description="Pearson correlation coefficients between academic, lifestyle, and attendance variables."
        >
          <CorrelationHeatmap
            features={correlations.features}
            correlationMatrix={correlations.correlation_matrix}
          />
        </ChartCard>
      )}

      {/* Academic Insights Row */}
      {insights.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-900">Computed Analytical Findings</h2>
            <span className="text-xs text-slate-500">(Derived strictly from cohort statistics)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {insights.map((ins, idx) => (
              <div key={idx} className="card bg-white border border-slate-200 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-semibold text-primary-700 uppercase tracking-wide bg-primary-50 px-2 py-0.5 rounded">
                      {ins.category}
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-900 text-sm">{ins.title}</h3>
                  <p className="text-xs text-slate-600 mt-2 leading-relaxed">{ins.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Ethical Disclaimer Footer Card */}
      <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-500 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-slate-400 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong>Academic & Ethical Disclaimer:</strong> GradeSense is developed strictly as a decision-support and
          research prototype for educational analytics. Model outputs represent statistical estimates derived from historical
          cohort observations and must never be treated as definitive judgments of personal capability or used as the sole
          determinant in academic evaluations.
        </p>
      </div>
    </div>
  );
}
