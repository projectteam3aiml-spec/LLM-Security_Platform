import React, { useEffect, useMemo, useState } from 'react';
import { Search, Loader2, AlertCircle } from 'lucide-react';
import { analysisService } from '../services/analysisService';

const DECISION_STYLE = {
  BLOCK: { label: 'Blocked', className: 'bg-red-50 text-red-600 border-red-100' },
  REVIEW: { label: 'Quarantined', className: 'bg-yellow-50 text-yellow-600 border-yellow-100' },
  ALLOW: { label: 'Allowed', className: 'bg-green-50 text-green-600 border-green-100' },
};

function formatTime(isoTimestamp) {
  return new Date(isoTimestamp).toLocaleString([], {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
}

export default function ThreatLogs() {
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    let isMounted = true;

    const loadLogs = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const data = await analysisService.getThreatLogs(100);
        if (isMounted) setEvents(data);
      } catch (error) {
        console.error('Failed to load threat logs:', error);
        if (isMounted) setErrorMessage('Could not load threat logs from the backend.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    loadLogs();
    return () => { isMounted = false; };
  }, []);

  const filteredEvents = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    if (!term) return events;
    return events.filter((row) =>
      row.prompt_text.toLowerCase().includes(term) ||
      row.source_system.toLowerCase().includes(term) ||
      (row.primary_threat || '').toLowerCase().includes(term)
    );
  }, [events, searchTerm]);

  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-8">

      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[#0d9488] text-xs font-bold tracking-widest uppercase">Audit Trail</span>
        </div>
        <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Threat logs</h2>
        <p className="text-slate-500 mt-1">Review every prompt decision with explainable security evidence.</p>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center gap-3">
          <AlertCircle size={20} />
          <p className="text-sm font-medium">{errorMessage}</p>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h3 className="text-base font-bold text-slate-900">All security events</h3>
            <p className="text-xs text-slate-500 mt-1">
              {isLoading ? 'Loading...' : `Showing ${filteredEvents.length} of ${events.length} recorded events`}
            </p>
          </div>
          <div className="relative">
            <input
              type="text"
              placeholder="Search events..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg w-72 focus:outline-none focus:ring-1 focus:ring-teal-500"
            />
            <Search size={16} className="text-gray-400 absolute left-3 top-2.5" />
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center gap-3 text-slate-500 py-16">
            <Loader2 size={24} className="animate-spin text-[#0d9488]" />
            <span className="font-medium">Loading threat logs...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-gray-50 text-slate-500 font-semibold text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">Time</th>
                  <th className="px-6 py-4">Source</th>
                  <th className="px-6 py-4">Prompt Preview</th>
                  <th className="px-6 py-4">Detection</th>
                  <th className="px-6 py-4">Risk</th>
                  <th className="px-6 py-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-slate-600">
                {filteredEvents.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-slate-400">
                      {events.length === 0
                        ? 'No security events recorded yet. Try the Analyze Prompt page.'
                        : 'No events match your search.'}
                    </td>
                  </tr>
                ) : (
                  filteredEvents.map((row) => {
                    const style = DECISION_STYLE[row.decision] || DECISION_STYLE.ALLOW;
                    return (
                      <tr key={row.id} className="hover:bg-slate-50">
                        <td className="px-6 py-4 text-slate-400 font-mono text-xs">{formatTime(row.timestamp)}</td>
                        <td className="px-6 py-4 font-medium">{row.source_system}</td>
                        <td className="px-6 py-4 text-slate-500 truncate max-w-[300px]">{row.prompt_text}</td>
                        <td className="px-6 py-4">
                          <span className="text-teal-600 font-medium">{row.primary_threat || 'Unknown'}</span>
                        </td>
                        <td className="px-6 py-4 font-mono font-bold">
                          <span className={row.risk_score_pct > 70 ? 'text-red-500' : 'text-green-500'}>{row.risk_score_pct}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-bold border ${style.className}`}>
                            {style.label}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
