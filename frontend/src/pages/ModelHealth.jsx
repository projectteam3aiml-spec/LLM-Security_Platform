import React, { useEffect, useState } from 'react';
import { ChevronRight, Loader2, AlertCircle } from 'lucide-react';
import { dashboardService } from '../services/dashboardService';

// Badge color/label is configurable per-tile so every tile reflects real
// computed status (see the four *Status computations below) instead of
// always showing a decorative green "Healthy".
const BADGE_STYLES = {
  green: 'text-[#10b981] bg-[#f0fdf4] border-[#bbf7d0]',
  amber: 'text-amber-700 bg-amber-50 border-amber-200',
  red: 'text-red-700 bg-red-50 border-red-200',
  slate: 'text-slate-500 bg-slate-100 border-slate-200',
};

const HealthMetric = ({ title, value, subtext, statusLabel = 'Healthy', badgeVariant = 'green', fillPct = 85, extra }) => (
  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
    <div className="flex justify-between items-start mb-6">
      <h3 className="text-sm font-bold text-slate-700">{title}</h3>
      <span className={`text-xs font-bold px-2 py-1 rounded-md border ${BADGE_STYLES[badgeVariant]}`}>{statusLabel}</span>
    </div>
    <div>
      <h2 className="text-4xl font-bold text-slate-900">{value}</h2>
      <div className="flex justify-between items-end mt-2">
        <p className="text-xs text-slate-500">{subtext}</p>
        <div className="w-1/2 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className="h-full bg-[#0d9488] rounded-full" style={{ width: `${fillPct}%` }}></div>
        </div>
      </div>
      {extra && <div className="mt-3 pt-3 border-t border-slate-100">{extra}</div>}
    </div>
  </div>
);

const PipelineStage = ({ step, title, loaded }) => (
  <div className="flex flex-col p-4 bg-slate-50 rounded-lg border border-gray-200 flex-1 relative">
    <span className="text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">{step}</span>
    <h4 className="text-sm font-bold text-slate-800 mb-4">{title}</h4>
    <span className={`text-xs font-medium ${loaded ? 'text-[#0d9488]' : 'text-slate-400'}`}>
      {loaded ? 'Loaded' : 'Not loaded yet'}
    </span>
  </div>
);

function formatUptime(seconds) {
  if (seconds == null) return '—';
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  if (hrs > 0) return `${hrs}h ${mins}m`;
  return `${mins}m`;
}

export default function ModelHealth() {
  const [health, setHealth] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const loadHealth = async () => {
      try {
        const data = await dashboardService.getModelHealth();
        if (isMounted) {
          setHealth(data);
          setErrorMessage(null);
        }
      } catch (error) {
        console.error('Failed to load model health:', error);
        if (isMounted) setErrorMessage('Could not reach the backend health endpoint.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    loadHealth();
    // Live-ish view: refresh every 15s while the page is open.
    const interval = setInterval(loadHealth, 15000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-[80vh] items-center justify-center text-slate-500 flex-col gap-4">
        <Loader2 size={32} className="animate-spin text-[#0d9488]" />
        <p className="font-medium">Checking model health...</p>
      </div>
    );
  }

  const pipeline = health?.pipeline;
  const p95 = health?.p95_latency_ms;
  const P95_TARGET_MS = 3000;
  const p95Status =
    p95 == null
      ? { label: 'No data', variant: 'slate' }
      : p95 <= P95_TARGET_MS
        ? { label: 'Healthy', variant: 'green' }
        : { label: 'Degraded', variant: 'amber' };

  // "Unreachable/uninitialized" for all four tiles below means the same
  // thing: the single /dashboard/model-health fetch this page makes never
  // returned data (still loading forever, or every attempt errored) --
  // `health` stays null in exactly that case, so each status check starts
  // from it rather than duplicating a separate reachability flag per tile.
  const promptsStatus =
    health == null
      ? { label: 'No data', variant: 'slate' }
      : health.status === 'Operational' && health.prompts_analyzed >= 0
        ? { label: 'Healthy', variant: 'green' }
        : { label: 'No data', variant: 'slate' };

  // Threshold applies to the end-to-end pipeline figure (the number that
  // actually reflects live classifier+PHI+threshold behavior together),
  // not the standalone classifier figure above it -- 85% chosen from the
  // user's suggested 80-85% range, just above this session's measured
  // 86.5% so "Healthy" is a real pass, not a trivial one.
  const ACCURACY_TARGET_PCT = 85;
  const endToEndAccuracyPct = health?.end_to_end_accuracy ? parseFloat(health.end_to_end_accuracy) : null;
  const accuracyStatus =
    endToEndAccuracyPct == null || Number.isNaN(endToEndAccuracyPct)
      ? { label: 'No data', variant: 'slate' }
      : endToEndAccuracyPct >= ACCURACY_TARGET_PCT
        ? { label: 'Healthy', variant: 'green' }
        : { label: 'Degraded', variant: 'amber' };

  const CPU_TARGET_PCT = 80;
  const MEMORY_TARGET_PCT = 85;
  const CRITICAL_PCT = 95;
  const resourceStatus =
    health == null
      ? { label: 'No data', variant: 'slate' }
      : health.cpu_usage_pct > CRITICAL_PCT || health.memory_usage_pct > CRITICAL_PCT
        ? { label: 'Critical', variant: 'red' }
        : health.cpu_usage_pct >= CPU_TARGET_PCT || health.memory_usage_pct >= MEMORY_TARGET_PCT
          ? { label: 'Degraded', variant: 'amber' }
          : { label: 'Healthy', variant: 'green' };

  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-8">

      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[#0d9488] text-xs font-bold tracking-widest uppercase">System Observability</span>
        </div>
        <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Model health</h2>
        <p className="text-slate-500 mt-1">Operational quality and detection performance across the security pipeline.</p>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center gap-3">
          <AlertCircle size={20} />
          <p className="text-sm font-medium">{errorMessage}</p>
        </div>
      )}

      <div className="grid grid-cols-4 gap-6">
        <HealthMetric
          title="Prompts scanned"
          value={health?.prompts_analyzed ?? 0}
          subtext="All-time total"
          statusLabel={promptsStatus.label}
          badgeVariant={promptsStatus.variant}
        />
        <HealthMetric
          title="Detection accuracy"
          value={health?.detection_accuracy ?? '—'}
          subtext="Standalone Classifier Base Accuracy"
          statusLabel={accuracyStatus.label}
          badgeVariant={accuracyStatus.variant}
          extra={
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-slate-500">End-to-End Pipeline Accuracy</span>
              <span className="text-sm font-bold text-slate-900">{health?.end_to_end_accuracy ?? '—'}</span>
            </div>
          }
        />
        <HealthMetric
          title="P95 latency"
          value={p95 != null ? `${p95} ms` : 'Collecting...'}
          subtext={`Target < ${P95_TARGET_MS} ms`}
          statusLabel={p95Status.label}
          badgeVariant={p95Status.variant}
        />
        <HealthMetric
          title="CPU / memory"
          value={health ? `${Math.round(health.cpu_usage_pct)}% / ${Math.round(health.memory_usage_pct)}%` : '—'}
          subtext={`Uptime: ${formatUptime(health?.uptime_seconds)}`}
          fillPct={health?.memory_usage_pct ?? 0}
          statusLabel={resourceStatus.label}
          badgeVariant={resourceStatus.variant}
        />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-base font-bold text-slate-900">Security pipeline</h3>
            <p className="text-xs text-slate-500 mt-1">
              {health?.status === 'Operational' ? 'All detection modules are operational' : 'Status unavailable'}
            </p>
          </div>
          <span className="flex items-center gap-1.5 text-xs font-bold text-green-700 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Live
          </span>
        </div>

        <div className="flex items-center gap-2 mt-4">
          <PipelineStage step="01" title="Preprocessor" loaded />
          <ChevronRight className="text-slate-300 flex-shrink-0" size={20} />
          <PipelineStage step="02" title="DistilBERT classifier" loaded={pipeline?.classifier_loaded} />
          <ChevronRight className="text-slate-300 flex-shrink-0" size={20} />
          <PipelineStage step="03" title="PII detector" loaded={pipeline?.phi_detector_loaded} />
          <ChevronRight className="text-slate-300 flex-shrink-0" size={20} />
          <PipelineStage step="04" title="Similarity engine" loaded={pipeline?.similarity_analyzer_loaded} />
          <ChevronRight className="text-slate-300 flex-shrink-0" size={20} />
          <PipelineStage step="05" title="Risk engine" loaded />
          <ChevronRight className="text-slate-300 flex-shrink-0" size={20} />
          <PipelineStage step="06" title="Policy decision" loaded />
        </div>
      </div>

    </div>
  );
}
