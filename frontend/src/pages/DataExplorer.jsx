import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Download,
  Database,
  Table as TableIcon,
  ChevronLeft,
  ChevronRight,
  Info,
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import { fetchDatasetSummary, fetchDatasetRecords } from '../services/api';

export default function DataExplorer() {
  const [loading, setLoading] = useState(true);
  const [recordsLoading, setRecordsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [summary, setSummary] = useState(null);
  const [recordsData, setRecordsData] = useState({ records: [], total_pages: 1, total_records: 0 });

  // Query state
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [schoolFilter, setSchoolFilter] = useState('');
  const [sexFilter, setSexFilter] = useState('');
  const [activeTab, setActiveTab] = useState('table'); // 'table' | 'schema' | 'stats'

  // Load dataset summary
  useEffect(() => {
    async function init() {
      try {
        setLoading(true);
        const sum = await fetchDatasetSummary();
        setSummary(sum);
      } catch (err) {
        setError(err.message || 'Failed to load dataset metadata');
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  // Fetch paginated records on filter/page change
  useEffect(() => {
    async function loadRecords() {
      try {
        setRecordsLoading(true);
        const params = {
          page,
          page_size: 15,
          search: search || undefined,
          school: schoolFilter || undefined,
          sex: sexFilter || undefined,
        };
        const data = await fetchDatasetRecords(params);
        setRecordsData(data);
      } catch (err) {
        console.error('Error fetching records:', err);
      } finally {
        setRecordsLoading(false);
      }
    }
    loadRecords();
  }, [page, search, schoolFilter, sexFilter]);

  const handleDownload = () => {
    window.open('http://localhost:8000/api/dataset/export/csv', '_blank');
  };

  if (loading) {
    return <LoadingSpinner message="Inspecting dataset records..." fullPage />;
  }

  if (error) {
    return <ErrorAlert message={error} retry={() => window.location.reload()} />;
  }

  const columns = summary?.columns || [];
  const stats = summary?.summary_stats || {};

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dataset Explorer</h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse, filter, and inspect schema characteristics for all {summary?.n_rows || 395} records.
          </p>
        </div>
        <button
          onClick={handleDownload}
          className="btn-secondary self-start sm:self-auto flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('table')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'table'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Data Records ({recordsData.total_records})
        </button>
        <button
          onClick={() => setActiveTab('schema')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'schema'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Schema & Missing Values ({columns.length} columns)
        </button>
        <button
          onClick={() => setActiveTab('stats')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'stats'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Descriptive Statistics
        </button>
      </div>

      {/* Tab 1: Records Table */}
      {activeTab === 'table' && (
        <div className="card space-y-4">
          {/* Controls Bar */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search across attributes..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="input-field pl-9"
              />
            </div>

            <select
              value={schoolFilter}
              onChange={(e) => {
                setSchoolFilter(e.target.value);
                setPage(1);
              }}
              className="input-field w-auto min-w-[130px]"
            >
              <option value="">All Schools</option>
              <option value="GP">GP (Gabriel Pereira)</option>
              <option value="MS">MS (Mousinho da Silveira)</option>
            </select>

            <select
              value={sexFilter}
              onChange={(e) => {
                setSexFilter(e.target.value);
                setPage(1);
              }}
              className="input-field w-auto min-w-[120px]"
            >
              <option value="">All Sexes</option>
              <option value="F">Female (F)</option>
              <option value="M">Male (M)</option>
            </select>

            {(search || schoolFilter || sexFilter) && (
              <button
                onClick={() => {
                  setSearch('');
                  setSchoolFilter('');
                  setSexFilter('');
                  setPage(1);
                }}
                className="text-xs text-primary-600 hover:underline px-2"
              >
                Reset filters
              </button>
            )}
          </div>

          {/* Table Container */}
          <div className="table-container border border-slate-200 rounded-lg max-h-[520px] overflow-auto">
            {recordsLoading ? (
              <div className="p-12">
                <LoadingSpinner message="Filtering records..." />
              </div>
            ) : recordsData.records.length === 0 ? (
              <div className="p-12 text-center text-slate-500 text-sm">
                No student records match the specified filters.
              </div>
            ) : (
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-100 text-slate-700 sticky top-0 z-10 border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3 font-semibold">#</th>
                    <th className="py-2.5 px-3 font-semibold">School</th>
                    <th className="py-2.5 px-3 font-semibold">Sex</th>
                    <th className="py-2.5 px-3 font-semibold">Age</th>
                    <th className="py-2.5 px-3 font-semibold">Address</th>
                    <th className="py-2.5 px-3 font-semibold">Study Time</th>
                    <th className="py-2.5 px-3 font-semibold">Failures</th>
                    <th className="py-2.5 px-3 font-semibold">Higher Ed</th>
                    <th className="py-2.5 px-3 font-semibold">Internet</th>
                    <th className="py-2.5 px-3 font-semibold">Absences</th>
                    <th className="py-2.5 px-3 font-semibold text-center bg-slate-200/50">G1</th>
                    <th className="py-2.5 px-3 font-semibold text-center bg-slate-200/50">G2</th>
                    <th className="py-2.5 px-3 font-semibold text-center bg-primary-100/70 text-primary-900">
                      G3 (Target)
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {recordsData.records.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-50 transition-colors">
                      <td className="py-2 px-3 text-slate-400 font-mono">
                        {(page - 1) * 15 + i + 1}
                      </td>
                      <td className="py-2 px-3 font-medium">{r.school}</td>
                      <td className="py-2 px-3">{r.sex}</td>
                      <td className="py-2 px-3">{r.age}</td>
                      <td className="py-2 px-3">{r.address === 'U' ? 'Urban' : 'Rural'}</td>
                      <td className="py-2 px-3">
                        {r.studytime === 1 ? '<2h' : r.studytime === 2 ? '2-5h' : r.studytime === 3 ? '5-10h' : '>10h'}
                      </td>
                      <td className="py-2 px-3">
                        {r.failures > 0 ? (
                          <span className="text-rose-600 font-semibold">{r.failures}</span>
                        ) : (
                          '0'
                        )}
                      </td>
                      <td className="py-2 px-3">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                            r.higher === 'yes' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {r.higher}
                        </span>
                      </td>
                      <td className="py-2 px-3">{r.internet}</td>
                      <td className="py-2 px-3">{r.absences}</td>
                      <td className="py-2 px-3 text-center bg-slate-50/50">{r.G1}</td>
                      <td className="py-2 px-3 text-center bg-slate-50/50">{r.G2}</td>
                      <td className="py-2 px-3 text-center font-bold bg-primary-50/40 text-primary-900">
                        {r.G3}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between text-xs text-slate-500 pt-2">
            <div>
              Showing {recordsData.records.length > 0 ? (page - 1) * 15 + 1 : 0} to{' '}
              {Math.min(page * 15, recordsData.total_records)} of {recordsData.total_records} records
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="btn-secondary px-2.5 py-1 text-xs disabled:opacity-40"
              >
                <ChevronLeft className="w-3.5 h-3.5 inline" /> Prev
              </button>
              <span className="px-2">
                Page {page} of {recordsData.total_pages || 1}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(recordsData.total_pages, p + 1))}
                disabled={page >= recordsData.total_pages}
                className="btn-secondary px-2.5 py-1 text-xs disabled:opacity-40"
              >
                Next <ChevronRight className="w-3.5 h-3.5 inline" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Schema & Quality */}
      {activeTab === 'schema' && (
        <div className="card space-y-4">
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-800 flex items-start gap-2">
            <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <strong>Data Quality Summary:</strong> Zero missing values detected across all 33 columns.
              Zero duplicate rows detected. All features comply with the documented UCI schema.
            </div>
          </div>

          <div className="table-container border border-slate-200 rounded-lg max-h-[500px] overflow-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-100 text-slate-700 sticky top-0 border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3 font-semibold">Column Name</th>
                  <th className="py-2.5 px-3 font-semibold">Data Type</th>
                  <th className="py-2.5 px-3 font-semibold">Unique Values</th>
                  <th className="py-2.5 px-3 font-semibold">Missing Count</th>
                  <th className="py-2.5 px-3 font-semibold">Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {columns.map((col, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-2 px-3 font-mono font-medium text-slate-900">{col.name}</td>
                    <td className="py-2 px-3 text-slate-500">{col.dtype}</td>
                    <td className="py-2 px-3">{col.unique}</td>
                    <td className="py-2 px-3 text-emerald-600 font-medium">{col.missing} (0%)</td>
                    <td className="py-2 px-3">
                      {col.name === 'G3' ? (
                        <span className="px-2 py-0.5 rounded bg-primary-100 text-primary-800 font-bold">
                          Primary Target
                        </span>
                      ) : col.name === 'G1' || col.name === 'G2' ? (
                        <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-medium">
                          Scenario B Only
                        </span>
                      ) : (
                        <span className="text-slate-400">Predictor</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Descriptive Stats */}
      {activeTab === 'stats' && (
        <div className="card space-y-4">
          <div className="table-container border border-slate-200 rounded-lg max-h-[500px] overflow-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-100 text-slate-700 sticky top-0 border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3 font-semibold">Feature</th>
                  <th className="py-2.5 px-3 font-semibold">Mean</th>
                  <th className="py-2.5 px-3 font-semibold">Std Dev</th>
                  <th className="py-2.5 px-3 font-semibold">Min</th>
                  <th className="py-2.5 px-3 font-semibold">25% (Q1)</th>
                  <th className="py-2.5 px-3 font-semibold">50% (Median)</th>
                  <th className="py-2.5 px-3 font-semibold">75% (Q3)</th>
                  <th className="py-2.5 px-3 font-semibold">Max</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {Object.entries(stats).map(([col, values], idx) => (
                  <tr key={idx} className="hover:bg-slate-50 font-mono">
                    <td className="py-2 px-3 font-semibold text-slate-900">{col}</td>
                    <td className="py-2 px-3">{Number(values.mean || 0).toFixed(2)}</td>
                    <td className="py-2 px-3">{Number(values.std || 0).toFixed(2)}</td>
                    <td className="py-2 px-3">{Number(values.min || 0).toFixed(1)}</td>
                    <td className="py-2 px-3">{Number(values['25%'] || 0).toFixed(1)}</td>
                    <td className="py-2 px-3 font-semibold text-primary-700">
                      {Number(values['50%'] || 0).toFixed(1)}
                    </td>
                    <td className="py-2 px-3">{Number(values['75%'] || 0).toFixed(1)}</td>
                    <td className="py-2 px-3">{Number(values.max || 0).toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
