import React, { useState } from 'react';
import {
  Calculator,
  Layers,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  Info,
  ShieldCheck,
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import { predictStudent } from '../services/api';

const DEFAULT_FEATURES = {
  school: 'GP',
  sex: 'F',
  age: 17,
  address: 'U',
  famsize: 'GT3',
  Pstatus: 'T',
  Medu: 3,
  Fedu: 3,
  Mjob: 'other',
  Fjob: 'services',
  reason: 'course',
  guardian: 'mother',
  traveltime: 1,
  studytime: 2,
  failures: 0,
  schoolsup: 'no',
  famsup: 'yes',
  paid: 'no',
  activities: 'yes',
  nursery: 'yes',
  higher: 'yes',
  internet: 'yes',
  romantic: 'no',
  famrel: 4,
  freetime: 3,
  goout: 2,
  Dalc: 1,
  Walc: 1,
  health: 4,
  absences: 4,
  G1: 12,
  G2: 13,
};

export default function Prediction() {
  const [scenario, setScenario] = useState('early_performance'); // 'early_performance' | 'grade_assisted'
  const [formData, setFormData] = useState(DEFAULT_FEATURES);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        scenario,
        features: {
          ...formData,
          age: Number(formData.age),
          Medu: Number(formData.Medu),
          Fedu: Number(formData.Fedu),
          traveltime: Number(formData.traveltime),
          studytime: Number(formData.studytime),
          failures: Number(formData.failures),
          famrel: Number(formData.famrel),
          freetime: Number(formData.freetime),
          goout: Number(formData.goout),
          Dalc: Number(formData.Dalc),
          Walc: Number(formData.Walc),
          health: Number(formData.health),
          absences: Number(formData.absences),
          G1: scenario === 'grade_assisted' ? Number(formData.G1) : undefined,
          G2: scenario === 'grade_assisted' ? Number(formData.G2) : undefined,
        },
      };

      const res = await predictStudent(payload);
      setResult(res);
    } catch (err) {
      setError(err.message || 'Prediction failed. Please verify inputs.');
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (presetName) => {
    if (presetName === 'high_achiever') {
      setFormData({
        ...DEFAULT_FEATURES,
        studytime: 4,
        failures: 0,
        higher: 'yes',
        Medu: 4,
        Fedu: 4,
        absences: 1,
        G1: 17,
        G2: 18,
      });
    } else if (presetName === 'struggling') {
      setFormData({
        ...DEFAULT_FEATURES,
        studytime: 1,
        failures: 2,
        higher: 'no',
        absences: 14,
        G1: 7,
        G2: 8,
      });
    } else {
      setFormData(DEFAULT_FEATURES);
    }
    setResult(null);
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Student Grade Prediction</h1>
        <p className="text-sm text-slate-500 mt-1">
          Predict student final academic outcomes (G3, 0–20 scale) using trained machine learning pipelines.
        </p>
      </div>

      {/* Scenario Selector Tabs */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={() => {
            setScenario('early_performance');
            setResult(null);
          }}
          className={`flex-1 p-4 rounded-xl border text-left transition-all ${
            scenario === 'early_performance'
              ? 'border-amber-500 bg-amber-50/50 ring-2 ring-amber-500/20 shadow-sm'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <div className="flex items-center gap-2">
            <Layers className={`w-5 h-5 ${scenario === 'early_performance' ? 'text-amber-600' : 'text-slate-400'}`} />
            <span className="font-semibold text-slate-900 text-sm">Scenario A: Early-Performance</span>
          </div>
          <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
            Predict G3 <strong>without</strong> prior term grades (G1, G2). Useful at beginning of school year.
          </p>
        </button>

        <button
          onClick={() => {
            setScenario('grade_assisted');
            setResult(null);
          }}
          className={`flex-1 p-4 rounded-xl border text-left transition-all ${
            scenario === 'grade_assisted'
              ? 'border-emerald-500 bg-emerald-50/50 ring-2 ring-emerald-500/20 shadow-sm'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <div className="flex items-center gap-2">
            <CheckCircle className={`w-5 h-5 ${scenario === 'grade_assisted' ? 'text-emerald-600' : 'text-slate-400'}`} />
            <span className="font-semibold text-slate-900 text-sm">Scenario B: Grade-Assisted</span>
          </div>
          <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
            Predict G3 <strong>with</strong> period grades G1 and G2. Higher precision for mid-year counseling.
          </p>
        </button>
      </div>

      {/* Preset Profiles */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-slate-500 font-medium">Quick Presets:</span>
        <button
          type="button"
          onClick={() => loadPreset('default')}
          className="px-2.5 py-1 rounded bg-slate-200/70 hover:bg-slate-300 text-slate-700 font-medium transition-colors"
        >
          Average Student
        </button>
        <button
          type="button"
          onClick={() => loadPreset('high_achiever')}
          className="px-2.5 py-1 rounded bg-emerald-100 hover:bg-emerald-200 text-emerald-800 font-medium transition-colors"
        >
          High Achiever Profile
        </button>
        <button
          type="button"
          onClick={() => loadPreset('struggling')}
          className="px-2.5 py-1 rounded bg-rose-100 hover:bg-rose-200 text-rose-800 font-medium transition-colors"
        >
          At-Risk Profile
        </button>
      </div>

      {/* Form & Results Container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Inputs (2 Cols) */}
        <form onSubmit={handlePredict} className="lg:col-span-2 card space-y-6">
          <h2 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center justify-between">
            <span>Student Attributes</span>
            <span className="text-xs font-normal text-slate-500">
              {scenario === 'early_performance' ? '30 Features' : '32 Features (with G1 & G2)'}
            </span>
          </h2>

          {/* Group 1: Academic & Term Grades */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-primary-700 uppercase tracking-wider">
              Academic & Term Assessments
            </h3>

            {scenario === 'grade_assisted' && (
              <div className="p-3 bg-emerald-50/50 border border-emerald-200 rounded-lg grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="label">
                    Period 1 Grade (G1, 0–20) <span className="text-emerald-600 font-bold">*</span>
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="20"
                    value={formData.G1}
                    onChange={(e) => handleInputChange('G1', e.target.value)}
                    className="input-field border-emerald-300 focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="label">
                    Period 2 Grade (G2, 0–20) <span className="text-emerald-600 font-bold">*</span>
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="20"
                    value={formData.G2}
                    onChange={(e) => handleInputChange('G2', e.target.value)}
                    className="input-field border-emerald-300 focus:border-emerald-500"
                    required
                  />
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="label">Weekly Study Time</label>
                <select
                  value={formData.studytime}
                  onChange={(e) => handleInputChange('studytime', e.target.value)}
                  className="input-field"
                >
                  <option value={1}>&lt; 2 hours</option>
                  <option value={2}>2 to 5 hours</option>
                  <option value={3}>5 to 10 hours</option>
                  <option value={4}>&gt; 10 hours</option>
                </select>
              </div>

              <div>
                <label className="label">Past Class Failures</label>
                <select
                  value={formData.failures}
                  onChange={(e) => handleInputChange('failures', e.target.value)}
                  className="input-field"
                >
                  <option value={0}>0 failures</option>
                  <option value={1}>1 failure</option>
                  <option value={2}>2 failures</option>
                  <option value={3}>3 failures</option>
                  <option value={4}>4 failures</option>
                </select>
              </div>

              <div>
                <label className="label">School Absences (0–93)</label>
                <input
                  type="number"
                  min="0"
                  max="93"
                  value={formData.absences}
                  onChange={(e) => handleInputChange('absences', e.target.value)}
                  className="input-field"
                  required
                />
              </div>
            </div>
          </div>

          {/* Group 2: Demographic & Family Background */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Demographic & Family Environment
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <label className="label">School</label>
                <select
                  value={formData.school}
                  onChange={(e) => handleInputChange('school', e.target.value)}
                  className="input-field"
                >
                  <option value="GP">GP (Gabriel Pereira)</option>
                  <option value="MS">MS (Mousinho)</option>
                </select>
              </div>

              <div>
                <label className="label">Sex</label>
                <select
                  value={formData.sex}
                  onChange={(e) => handleInputChange('sex', e.target.value)}
                  className="input-field"
                >
                  <option value="F">Female (F)</option>
                  <option value="M">Male (M)</option>
                </select>
              </div>

              <div>
                <label className="label">Age (15–22)</label>
                <input
                  type="number"
                  min="15"
                  max="22"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', e.target.value)}
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="label">Address</label>
                <select
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  className="input-field"
                >
                  <option value="U">Urban (U)</option>
                  <option value="R">Rural (R)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <label className="label">Mother Education</label>
                <select
                  value={formData.Medu}
                  onChange={(e) => handleInputChange('Medu', e.target.value)}
                  className="input-field"
                >
                  <option value={0}>0 - None</option>
                  <option value={1}>1 - Primary (4th gr)</option>
                  <option value={2}>2 - 5th to 9th gr</option>
                  <option value={3}>3 - Secondary</option>
                  <option value={4}>4 - Higher Education</option>
                </select>
              </div>

              <div>
                <label className="label">Father Education</label>
                <select
                  value={formData.Fedu}
                  onChange={(e) => handleInputChange('Fedu', e.target.value)}
                  className="input-field"
                >
                  <option value={0}>0 - None</option>
                  <option value={1}>1 - Primary (4th gr)</option>
                  <option value={2}>2 - 5th to 9th gr</option>
                  <option value={3}>3 - Secondary</option>
                  <option value={4}>4 - Higher Education</option>
                </select>
              </div>

              <div>
                <label className="label">Mother Job</label>
                <select
                  value={formData.Mjob}
                  onChange={(e) => handleInputChange('Mjob', e.target.value)}
                  className="input-field"
                >
                  <option value="teacher">Teacher</option>
                  <option value="health">Health</option>
                  <option value="services">Services</option>
                  <option value="at_home">At home</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="label">Father Job</label>
                <select
                  value={formData.Fjob}
                  onChange={(e) => handleInputChange('Fjob', e.target.value)}
                  className="input-field"
                >
                  <option value="teacher">Teacher</option>
                  <option value="health">Health</option>
                  <option value="services">Services</option>
                  <option value="at_home">At home</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          {/* Group 3: Support, Lifestyle & Alcohol */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Educational Support & Lifestyle
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <label className="label">Higher Education</label>
                <select
                  value={formData.higher}
                  onChange={(e) => handleInputChange('higher', e.target.value)}
                  className="input-field"
                >
                  <option value="yes">Yes</option>
                  <option value="no">No</option>
                </select>
              </div>

              <div>
                <label className="label">Internet Access</label>
                <select
                  value={formData.internet}
                  onChange={(e) => handleInputChange('internet', e.target.value)}
                  className="input-field"
                >
                  <option value="yes">Yes</option>
                  <option value="no">No</option>
                </select>
              </div>

              <div>
                <label className="label">Extra School Support</label>
                <select
                  value={formData.schoolsup}
                  onChange={(e) => handleInputChange('schoolsup', e.target.value)}
                  className="input-field"
                >
                  <option value="no">No</option>
                  <option value="yes">Yes</option>
                </select>
              </div>

              <div>
                <label className="label">Paid Classes</label>
                <select
                  value={formData.paid}
                  onChange={(e) => handleInputChange('paid', e.target.value)}
                  className="input-field"
                >
                  <option value="no">No</option>
                  <option value="yes">Yes</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <label className="label">Family Rel (1–5)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={formData.famrel}
                  onChange={(e) => handleInputChange('famrel', e.target.value)}
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="label">Going Out (1–5)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={formData.goout}
                  onChange={(e) => handleInputChange('goout', e.target.value)}
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="label">Workday Alc (1–5)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={formData.Dalc}
                  onChange={(e) => handleInputChange('Dalc', e.target.value)}
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="label">Weekend Alc (1–5)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={formData.Walc}
                  onChange={(e) => handleInputChange('Walc', e.target.value)}
                  className="input-field"
                  required
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={() => {
                setFormData(DEFAULT_FEATURES);
                setResult(null);
              }}
              className="btn-secondary flex items-center gap-1.5"
            >
              <RotateCcw className="w-4 h-4" /> Reset
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center gap-2 px-6 py-2.5"
            >
              {loading ? (
                <span>Predicting...</span>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run Prediction</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Prediction Results Panel (1 Col) */}
        <div className="space-y-4">
          <div className="card bg-gradient-to-b from-white to-slate-50 border border-slate-200 sticky top-20">
            <h2 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center gap-2">
              <Calculator className="w-5 h-5 text-primary-600" />
              <span>Prediction Result</span>
            </h2>

            {loading ? (
              <div className="py-12">
                <LoadingSpinner message="Evaluating through trained pipeline..." />
              </div>
            ) : error ? (
              <div className="py-4">
                <ErrorAlert message={error} />
              </div>
            ) : result ? (
              <div className="py-4 space-y-4 animate-fade-in">
                {/* Predicted Grade Callout */}
                <div className="text-center p-6 bg-slate-900 text-white rounded-xl shadow-inner">
                  <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold">
                    Predicted Final Grade (G3)
                  </p>
                  <p className="text-4xl font-extrabold tracking-tight mt-2 text-primary-300">
                    {result.predicted_grade.toFixed(2)}
                    <span className="text-lg text-slate-400 font-normal"> / 20</span>
                  </p>
                  <div className="mt-3 inline-block px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-white">
                    {result.grade_category}
                  </div>
                </div>

                {/* Metadata List */}
                <div className="space-y-2 text-xs text-slate-600">
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-400">Model Pipeline:</span>
                    <span className="font-semibold text-slate-800">{result.model_used}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-400">Prediction Scenario:</span>
                    <span className="font-semibold text-slate-800">
                      {result.scenario === 'early_performance' ? 'Scenario A (Early)' : 'Scenario B (Grade-Assisted)'}
                    </span>
                  </div>
                  {result.metrics_summary && (
                    <div className="flex justify-between py-1.5 border-b border-slate-100">
                      <span className="text-slate-400">Pipeline Test MAE:</span>
                      <span className="font-semibold text-slate-800">
                        &plusmn;{result.metrics_summary.MAE.toFixed(2)} pts
                      </span>
                    </div>
                  )}
                </div>

                {/* Interpretation */}
                <div className="p-3 bg-primary-50/50 border border-primary-200/60 rounded-lg text-xs text-slate-700 leading-relaxed">
                  <div className="flex items-center gap-1.5 font-semibold text-primary-900 mb-1">
                    <Info className="w-3.5 h-3.5" />
                    <span>Cautious Academic Interpretation</span>
                  </div>
                  {result.interpretation}
                </div>

                {/* Reset button */}
                <button
                  type="button"
                  onClick={() => setResult(null)}
                  className="w-full btn-secondary text-xs py-2"
                >
                  Clear Result
                </button>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400 text-xs">
                <Calculator className="w-10 h-10 mx-auto text-slate-300 mb-2" />
                <p>Adjust student parameters and click &ldquo;Run Prediction&rdquo; to estimate final grade outcome.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
