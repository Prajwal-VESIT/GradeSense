import React, { useState, useEffect } from 'react';
import {
  Lightbulb,
  CheckCircle,
  AlertTriangle,
  FileCheck,
  TrendingUp,
  Clock,
  UserCheck,
  ShieldAlert,
  GraduationCap,
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import { fetchInsights } from '../services/api';

export default function Insights() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [insights, setInsights] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const res = await fetchInsights();
        setInsights(res);
      } catch (err) {
        setError(err.message || 'Failed to load insights');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Synthesizing academic findings and recommendations..." fullPage />;
  }

  if (error) {
    return <ErrorAlert message={error} retry={() => window.location.reload()} />;
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Academic Insights & Institutional Recommendations</h1>
        <p className="text-sm text-slate-500 mt-1">
          Evidence-based analytical deductions derived from empirical data modeling and quantitative testing.
        </p>
      </div>

      {/* Analytical Findings Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-amber-500" />
          <span>Core Analytical Discoveries</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((item, idx) => (
            <div key={idx} className="card bg-white border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-primary-700 bg-primary-50 px-2 py-0.5 rounded uppercase">
                  {item.category}
                </span>
              </div>
              <h3 className="font-bold text-slate-900 text-sm">{item.title}</h3>
              <p className="text-xs text-slate-600 leading-relaxed">{item.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Concrete Recommendations Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-primary-600" />
          <span>Institutional Policy & Mentorship Recommendations</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card border-l-4 border-l-blue-500 space-y-2">
            <div className="flex items-center gap-2 text-blue-700 font-bold text-sm">
              <Clock className="w-4 h-4" />
              <span>Early Study-Skill Workshops</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Targeted study-habit interventions should be offered early in the academic calendar for students
              reporting &lt;2 hours of weekly independent study. Data shows dedicated study time correlates strongly
              with higher median final marks.
            </p>
          </div>

          <div className="card border-l-4 border-l-emerald-500 space-y-2">
            <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
              <FileCheck className="w-4 h-4" />
              <span>Mid-Semester Formative Milestones</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Period grades (G1 and G2) explain over 80% of final grade variation. Institutions should institute
              formal mid-semester academic counseling immediately upon publication of G1 results, giving struggling
              students actionable time to recover.
            </p>
          </div>

          <div className="card border-l-4 border-l-amber-500 space-y-2">
            <div className="flex items-center gap-2 text-amber-700 font-bold text-sm">
              <UserCheck className="w-4 h-4" />
              <span>Nuanced Absenteeism Monitoring</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Rather than punitive uniform attendance measures, differentiate occasional absences from chronic absenteeism.
              Severe attendance drops (&gt;20 classes missed) frequently co-occur with complete course abandonment (G3 = 0).
            </p>
          </div>
        </div>
      </div>

      {/* Limitations Section */}
      <div className="card bg-slate-50 border border-slate-200 space-y-3">
        <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600" />
          <span>Methodological Limitations & Constraints</span>
        </h2>
        <ul className="text-xs text-slate-600 space-y-2 list-disc list-inside leading-relaxed">
          <li>
            <strong>Geographic & Cultural Boundary:</strong> Dataset comprises 395 secondary students from the Alentejo
            region in Portugal. Cultural, pedagogical, and grading dynamics may differ across universities or nations.
          </li>
          <li>
            <strong>Correlation Does Not Imply Causation:</strong> Observable relationships between lifestyle factors
            (such as alcohol consumption or internet availability) represent empirical associations rather than direct causal drivers.
          </li>
          <li>
            <strong>Zero-Point Clumping:</strong> 38 students (9.6%) received a final grade of exactly 0. These records
            predominantly represent exam dropouts rather than gradual cognitive declines, which standard linear regressions
            consistently overestimate.
          </li>
        </ul>
      </div>

      {/* Ethical Governance Box */}
      <div className="p-5 bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-xl space-y-2">
        <div className="flex items-center gap-2 font-bold text-sm text-primary-300">
          <ShieldAlert className="w-4 h-4" />
          <span>Ethical Governance & Non-Discriminatory Use</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Educational analytics tools must never automate disciplinary or adverse academic exclusions.
          Sensitive demographic characteristics (such as parent marital status or family size) must never serve as grounds
          for punitive institutional decisions. GradeSense must function strictly as an auxiliary mentorship aid to expand
          academic support for vulnerable students.
        </p>
      </div>
    </div>
  );
}
