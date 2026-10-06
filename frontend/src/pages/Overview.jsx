import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Key, AlertCircle, Shield, CheckCircle2, Loader2 } from 'lucide-react';
import { dashboardService } from '../services/dashboardService';
import { analysisService } from '../services/analysisService';
import { useAuth } from '../hooks/useAuth';

const RISK_COLORS = { safe: '#10b981', suspicious: '#f59e0b', malicious: '#ef4444' };

const DECISION_STYLE = {
  BLOCK: { label: 'Blocked', className: 'bg-red-50 text-red-600 border-red-100' },
  REVIEW: { label: 'Quarantined', className: 'bg-yellow-50 text-yellow-600 border-yellow-100' },
  ALLOW: { label: 'Allowed', className: 'bg-green-50 text-green-600 border-green-100' },
};

function formatTime(isoTimestamp) {
  return new Date(isoTimestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function Overview() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [riskDistribution, setRiskDistribution] = useState(null);
  const [trends, setTrends] = useState([]);
  const [recentEvents, setRecentEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const [statsData, riskData, trendsData, logsData] = await Promise.all([
          dashboardService.getStats(),
          dashboardService.getRiskDistribution(),
          dashboardService.getThreatTrends(24),
          analysisService.getThreatLogs(5),
        ]);
        if (!isMounted) return;
        setStats(statsData);
        setRiskDistribution(riskData);
        setTrends(trendsData);
        setRecentEvents(logsData);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        if (isMounted) setErrorMessage('Could not load live metrics from the backend.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    loadDashboard();
    return () => { isMounted = false; };
  }, []);

  const riskData = riskDistribution
    ? [
        { name: 'Safe', value: riskDistribution.safe, color: RISK_COLORS.safe },
        { name: 'Suspicious', value: riskDistribution.suspicious, color: RISK_COLORS.suspicious },
        { name: 'Malicious', value: riskDistribution.malicious, color: RISK_COLORS.malicious },
      ]
    : [];
  const hasRiskData = riskData.some((entry) => entry.value > 0);
  const hasTrendData = trends.some((point) => point.blocked > 0 || point.flagged > 0);

  if (isLoading) {
    return (
      <div className="flex h-[80vh] items-center justify-center text-slate-500 flex-col gap-4">
        <Loader2 size={32} className="animate-spin text-[#0d9488]" />
        <p className="font-medium">Loading live security metrics...</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-6">

      {/* Header Section */}
      <div className="flex items-end justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-1.5 h-1.5 rounded-full bg-[#10b981]"></div>
            <span className="text-[#10b981] text-xs font-bold tracking-widest uppercase">Protection Active</span>
          </div>
          <h2 className="text-3xl font-bold text-slate-900 tracking-tight">
            Welcome{user?.email ? `, ${user.email.split('@')[0]}` : ''}
          </h2>
          <p className="text-slate-500 mt-1">Here's what your LLM security layer is seeing right now.</p>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center gap-3">
          <AlertCircle size={20} />
          <p className="text-sm font-medium">{errorMessage}</p>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-start justify-between mb-4">
            <div className="w-8 h-8 rounded-full bg-teal-50 text-teal-600 flex items-center justify-center">
              <Key size={16} />
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Prompts analyzed</p>
            <h3 className="text-3xl font-bold text-slate-900">{stats?.prompts_analyzed ?? 0}</h3>
            <p className="text-xs text-slate-400 mt-1">All-time total</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-start justify-between mb-4">
            <div className="w-8 h-8 rounded-full bg-red-50 text-red-500 flex items-center justify-center">
              <AlertCircle size={16} />
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Threats blocked</p>
            <h3 className="text-3xl font-bold text-slate-900">{stats?.threats_blocked ?? 0}</h3>
            <p className="text-xs text-slate-400 mt-1">
              {stats?.prompts_analyzed ? `${((stats.threats_blocked / stats.prompts_analyzed) * 100).toFixed(1)}% of all prompts` : 'No prompts yet'}
            </p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-start justify-between mb-4">
            <div className="w-8 h-8 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center">
              <Shield size={16} />
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">PII entities masked</p>
            <h3 className="text-3xl font-bold text-slate-900">{stats?.phi_entities_masked ?? 0}</h3>
            <p className="text-xs text-slate-400 mt-1">Across all analyzed prompts</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-start justify-between mb-4">
            <div className="w-8 h-8 rounded-full bg-green-50 text-green-500 flex items-center justify-center">
              <CheckCircle2 size={16} />
            </div>
            <span className="text-xs font-bold text-[#10b981] bg-[#f0fdf4] px-2 py-1 rounded-md border border-[#bbf7d0]">Healthy</span>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Average latency</p>
            <h3 className="text-3xl font-bold text-slate-900">
              {stats?.avg_latency_ms != null ? stats.avg_latency_ms : '—'}
              {stats?.avg_latency_ms != null && <span className="text-xl text-slate-500 font-medium ml-1">ms</span>}
            </h3>
            <p className="text-xs text-slate-400 mt-1">Across all requests</p>
          </div>
        </div>
      </div>

      {/* Middle Charts Section */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-base font-bold text-slate-900">Threat activity</h3>
              <p className="text-xs text-slate-500">Blocked and flagged prompts over the last 24 hours</p>
              <div className="flex items-center gap-4 mt-3">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-red-500"></div>
                  <span className="text-xs font-medium text-slate-600">Blocked</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-orange-400"></div>
                  <span className="text-xs font-medium text-slate-600">Flagged</span>
                </div>
              </div>
            </div>
          </div>
          <div className="h-64 relative">
            {!hasTrendData && (
              <div className="absolute inset-0 flex items-center justify-center text-sm text-slate-400 font-medium">
                No threat activity recorded in the last 24 hours
              </div>
            )}
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94a3b8' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
                <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Area type="monotone" dataKey="blocked" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorBlocked)" />
                <Area type="monotone" dataKey="flagged" stroke="#fb923c" strokeWidth={3} strokeDasharray="5 5" fill="none" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="col-span-1 bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
          <h3 className="text-base font-bold text-slate-900">Risk distribution</h3>
          <p className="text-xs text-slate-500 mb-6">Current prompt classification</p>

          <div className="flex-1 flex items-center justify-center relative">
            {hasRiskData ? (
              <>
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={riskData} innerRadius={55} outerRadius={75} paddingAngle={4} dataKey="value" stroke="none">
                      {riskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-2xl font-bold text-slate-900">{stats?.prompts_analyzed ?? 0}</span>
                  <span className="text-xs text-slate-500 font-medium">Total</span>
                </div>
              </>
            ) : (
              <p className="text-sm text-slate-400 font-medium">No prompts analyzed yet</p>
            )}
          </div>

          {hasRiskData && (
            <div className="space-y-3 mt-4 mb-6">
              {riskData.map((item) => (
                <div key={item.name} className="flex justify-between items-center text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                    <span className="text-slate-600 font-medium">{item.name}</span>
                  </div>
                  <span className="font-bold text-slate-900">{item.value}%</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Security Events Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-8">
        <div className="px-6 py-5 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recent security events</h3>
            <p className="text-xs text-slate-500 mt-1">Live analysis and policy actions</p>
          </div>
        </div>
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
              {recentEvents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-400">
                    No security events recorded yet. Try the Analyze Prompt page.
                  </td>
                </tr>
              ) : (
                recentEvents.map((row) => {
                  const style = DECISION_STYLE[row.decision] || DECISION_STYLE.ALLOW;
                  return (
                    <tr key={row.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 text-slate-400 font-mono text-xs">{formatTime(row.timestamp)}</td>
                      <td className="px-6 py-4 font-medium">{row.source_system}</td>
                      <td className="px-6 py-4 text-slate-500 truncate max-w-[250px]">{row.prompt_text}</td>
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
      </div>

    </div>
  );
}
