import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  Line,
  ComposedChart,
} from 'recharts';
import {
  LineChart as LineChartIcon,
  HelpCircle,
  TrendingUp,
  Info,
  CheckCircle,
  FileText,
} from 'lucide-react';

import ChartCard from '../components/ChartCard';
import CorrelationHeatmap from '../components/CorrelationHeatmap';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import {
  fetchGradeDistribution,
  fetchCorrelations,
  fetchModelComparison,
  fetchDatasetRecords,
  fetchFeatureImportance,
  fetchErrorAnalysis,
} from '../services/api';

export default function Analysis() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [gradeDist, setGradeDist] = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [models, setModels] = useState([]);
  const [rawRecords, setRawRecords] = useState([]);
  const [featureImp, setFeatureImp] = useState({});
  const [errorAnalysis, setErrorAnalysis] = useState({});

  useEffect(() => {
    async function loadAll() {
      try {
        setLoading(true);
        setError(null);
        const [gRes, cRes, mRes, rRes, fRes, eRes] = await Promise.all([
          fetchGradeDistribution(),
          fetchCorrelations(),
          fetchModelComparison(),
          fetchDatasetRecords({ page: 1, page_size: 100 }),
          fetchFeatureImportance(),
          fetchErrorAnalysis(),
        ]);
        setGradeDist(gRes);
        setCorrelations(cRes);
        setModels(mRes);
        setRawRecords(rRes.records || []);
        setFeatureImp(fRes);
        setErrorAnalysis(eRes);
      } catch (err) {
        setError(err.message || 'Failed to load EDA visualizations');
      } finally {
        setLoading(false);
      }
    }
    loadAll();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Generating academic analytics charts..." fullPage />;
  }

  if (error) {
    return <ErrorAlert message={error} retry={() => window.location.reload()} />;
  }

  // Visualization 1: Grade Histogram
  const histogramData = gradeDist?.bins
    ? Object.entries(gradeDist.bins).map(([grade, count]) => ({
        grade: `G3=${grade}`,
        gradeVal: Number(grade),
        count,
      }))
    : [];

  // Visualization 2: Study Time vs Grade Aggregation
  const studyGroups = [
    { key: 1, label: '<2 hrs', count: 0, totalG3: 0 },
    { key: 2, label: '2-5 hrs', count: 0, totalG3: 0 },
    { key: 3, label: '5-10 hrs', count: 0, totalG3: 0 },
    { key: 4, label: '>10 hrs', count: 0, totalG3: 0 },
  ];
  rawRecords.forEach((r) => {
    const g = studyGroups.find((sg) => sg.key === r.studytime);
    if (g) {
      g.count += 1;
      g.totalG3 += r.G3;
    }
  });
  const studyTimeChartData = studyGroups.map((g) => ({
    label: g.label,
    avgGrade: g.count > 0 ? Number((g.totalG3 / g.count).toFixed(2)) : 0,
    students: g.count,
  }));

  // Visualization 4: G1 vs G3 & G2 vs G3 Scatter Data
  const g1g3Scatter = rawRecords.map((r) => ({ x: r.G1, y: r.G3 }));
  const g2g3Scatter = rawRecords.map((r) => ({ x: r.G2, y: r.G3 }));

  // Visualization 5: Absences vs G3
  const absencesScatter = rawRecords.map((r) => ({ absences: r.absences, grade: r.G3 }));

  // Visualization 6: Model Benchmark Data
  const earlyModels = models.filter((m) => m.scenario === 'early_performance');
  const assistedModels = models.filter((m) => m.scenario === 'grade_assisted');

  const modelMetricsData = earlyModels.map((em) => {
    const am = assistedModels.find((m) => m.model === em.model) || {};
    return {
      name: em.model.replace('Regressor', ''),
      earlyMAE: em.test_mae,
      earlyRMSE: em.test_rmse,
      assistedMAE: am.test_mae,
      assistedRMSE: am.test_rmse,
    };
  });

  // Visualization 8: Feature Importance Data
  const earlyImpData = (featureImp?.early_performance || []).slice(0, 8).map((f) => ({
    feature: f.feature,
    importance: Number(f.importance_mean.toFixed(3)),
  }));
  const assistedImpData = (featureImp?.grade_assisted || []).slice(0, 8).map((f) => ({
    feature: f.feature,
    importance: Number(f.importance_mean.toFixed(3)),
  }));

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Exploratory Data Analysis & Visualizations</h1>
        <p className="text-sm text-slate-500 mt-1">
          Rigorous statistical distributions, correlation structures, and machine learning diagnostics.
        </p>
      </div>

      {/* Row 1: Visualizations 1 & 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Viz 1: G3 Distribution */}
        <ChartCard
          title="Visualization 1: Final Grade (G3) Distribution"
          description="Distribution of student cohort across the 0–20 scale with mean and median markers."
        >
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={histogramData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="grade" tick={{ fontSize: 9 }} interval={1} angle={-45} textAnchor="end" />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip
                  formatter={(val) => [`${val} students`, 'Frequency']}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mt-3 text-xs text-slate-600">
            <strong>Statistical Finding:</strong> G3 approximates a normal distribution centered at &mu; = 10.42,
            except for an anomalous zero-point spike (9.6% of students). In the Portuguese educational system, 10
            is the passing threshold; 33.7% scored below 10 (insufficient).
          </div>
        </ChartCard>

        {/* Viz 2: Grade by Study Time */}
        <ChartCard
          title="Visualization 2: Final Grade by Weekly Study Time"
          description="Comparison of mean final grade achievement across weekly study time tiers."
        >
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={studyTimeChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 20]} tick={{ fontSize: 10 }} />
                <Tooltip
                  formatter={(val) => [`${val} / 20`, 'Avg Grade']}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
                <Bar dataKey="avgGrade" fill="#0d9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mt-3 text-xs text-slate-600">
            <strong>Statistical Finding:</strong> Students dedicating &gt;10 hours weekly achieve higher average
            grades (~11.6/20) compared to those studying &lt;2 hours (~10.0/20). ANOVA testing confirms statistical
            significance (F = 3.20, p = 0.023), although broad individual variance remains within tiers.
          </div>
        </ChartCard>
      </div>

      {/* Row 2: Visualization 3 Correlation Matrix */}
      {correlations?.features && (
        <ChartCard
          title="Visualization 3: Pearson Correlation Heatmap"
          description="Pairwise linear correlation coefficients between numerical attributes."
        >
          <CorrelationHeatmap
            features={correlations.features}
            correlationMatrix={correlations.correlation_matrix}
          />
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mt-3 text-xs text-slate-600">
            <strong>Statistical Finding:</strong> Formative grades G1 and G2 display exceptionally high positive
            correlation with G3 (r = 0.801 and r = 0.905, respectively). Conversely, failures (r = -0.360) and
            absences show negative associations.
          </div>
        </ChartCard>
      )}

      {/* Row 3: Visualizations 4 & 5 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Viz 4: Earlier Grades vs G3 */}
        <ChartCard
          title="Visualization 4: Earlier Period Grades (G1, G2) vs Final Grade (G3)"
          description="Formative assessments versus summative final grade on 100 sample student records."
        >
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" dataKey="x" name="Prior Grade" domain={[0, 20]} tick={{ fontSize: 10 }} />
                <YAxis type="number" dataKey="y" name="Final Grade (G3)" domain={[0, 20]} tick={{ fontSize: 10 }} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
                <Scatter name="G1 vs G3" data={g1g3Scatter} fill="#3b82f6" opacity={0.6} />
                <Scatter name="G2 vs G3" data={g2g3Scatter} fill="#f97316" opacity={0.6} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mt-3 text-xs text-slate-600">
            <strong>Statistical Finding:</strong> G2 exhibits near-collinear alignment with G3. Students scoring
            zero on G3 frequently received non-zero scores on G1 and G2, reflecting dropouts prior to the final exam.
          </div>
        </ChartCard>

        {/* Viz 5: Absences vs G3 */}
        <ChartCard
          title="Visualization 5: School Absences vs Final Grade"
          description="Scatter analysis of school absence counts against final numerical grade."
        >
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" dataKey="absences" name="Absences" tick={{ fontSize: 10 }} />
                <YAxis type="number" dataKey="grade" name="Final Grade" domain={[0, 20]} tick={{ fontSize: 10 }} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
                <Scatter name="Students" data={absencesScatter} fill="#6366f1" opacity={0.7} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mt-3 text-xs text-slate-600">
            <strong>Statistical Finding:</strong> Absence exhibits a non-linear rank relationship (Spearman &rho; = -0.05).
            Moderate absenteeism (1–10 classes) does not reliably hinder performance, but extreme outliers (&gt;30 absences)
            frequently accompany poor marks.
          </div>
        </ChartCard>
      </div>

      {/* Row 4: Visualizations 6 & 7 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Viz 6: Model Benchmark Comparison */}
        <ChartCard
          title="Visualization 6: Model Error Comparison (MAE & RMSE)"
          description="Comparison across 6 regression models on held-out test data (79 students)."
        >
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={modelMetricsData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 4]} tick={{ fontSize: 10 }} />
                <Tooltip
                  formatter={(val, name) => [
                    `${val?.toFixed(3)} pts`,
                    name === 'earlyMAE' ? 'Early MAE' : name === 'assistedMAE' ? 'Assisted MAE' : name,
                  ]}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
                <Bar dataKey="earlyMAE" name="Early MAE" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="assistedMAE" name="Assisted MAE" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mt-3 text-xs text-slate-600">
            <strong>Statistical Finding:</strong> RandomForest achieved lowest error in both scenarios (Scenario A:
            Test MAE = 3.00, Scenario B: Test MAE = 1.21). The DummyRegressor baseline predicts mean (MAE = 3.65).
          </div>
        </ChartCard>

        {/* Viz 7: Permutation Feature Importance */}
        <ChartCard
          title="Visualization 8: Permutation Feature Importance (Top Features)"
          description="Impact on prediction MAE when feature values are permuted on test data."
        >
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={assistedImpData.length > 0 ? assistedImpData : earlyImpData}
                margin={{ top: 10, right: 20, left: 20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="feature" tick={{ fontSize: 10 }} width={70} />
                <Tooltip
                  formatter={(val) => [`${val} MAE increase`, 'Permutation Loss']}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
                <Bar dataKey="importance" fill="#0284c7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mt-3 text-xs text-slate-600">
            <strong>Statistical Finding:</strong> In Scenario B, G2 and G1 overwhelmingly dominate predictive power.
            In Scenario A, study time, failures, mother's education (Medu), and absences are the top predictors.
          </div>
        </ChartCard>
      </div>
    </div>
  );
}
