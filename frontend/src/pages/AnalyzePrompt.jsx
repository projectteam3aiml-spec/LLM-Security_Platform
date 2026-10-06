import React, { useMemo, useState } from 'react';
import { AlertCircle, RefreshCw, Send, Shield, Zap } from 'lucide-react';
import { analysisService } from '../services/analysisService';
import ExplanationPanel from '../components/analysis/ExplanationPanel';
import RiskGauge from '../components/analysis/RiskGauge';

const MAX_PROMPT_LENGTH = 4000;
const SESSION_STORAGE_KEY = 'llm_security_session_id';
// Measured directly against the real test set with the deployed weights --
// keep in sync with backend/app/ai_engine/classifier.py's TEST_ACCURACY.
const CLASSIFIER_TEST_ACCURACY = '89.9%';

// A stable per-browser id, persisted across page loads, so the backend's
// BehavioralAnomalyEngine can actually detect bursts/repeats across requests
// instead of seeing every request as a fresh, unrelated session.
function getSessionId() {
  let id = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!id) {
    id = crypto.randomUUID ? crypto.randomUUID() : `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem(SESSION_STORAGE_KEY, id);
  }
  return id;
}

export default function AnalyzePrompt() {
  const [prompt, setPrompt] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const sessionId = useMemo(getSessionId, []);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsAnalyzing(true);
    setError(null);
    setResults(null);

    try {
      const data = await analysisService.analyzePrompt({
        prompt,
        source: 'Web Console',
        session_id: sessionId,
      });
      setResults(data);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError('Failed to reach the AI Engine. Ensure the backend is running and reachable.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6 h-[calc(100vh-2rem)] flex flex-col">
      <div className="flex justify-between items-center">
        <div>
          <span className="text-indigo-600 text-xs font-bold tracking-widest uppercase">Real-time Security Test</span>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">Interactive Prompt Analysis</h1>
          <p className="text-sm text-slate-500 mt-1">
            Test prompts against the injection classifier, PHI/PII NER, adversarial-similarity, and healthcare rule layers in real time.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Left Column: Input and Sanitized Output */}
        <div className="lg:col-span-2 flex flex-col space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-1 flex flex-col h-64 shrink-0">
            <textarea
              className="w-full flex-1 p-4 bg-transparent resize-none outline-none text-slate-700 placeholder-slate-400"
              placeholder="Enter a prompt to analyze for injections, jailbreaks, or PHI/PII leaks..."
              value={prompt}
              maxLength={MAX_PROMPT_LENGTH}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={isAnalyzing}
            />
            <div className="flex justify-between items-center p-3 border-t border-slate-100 bg-slate-50 rounded-b-lg">
              <div className="flex items-center gap-3 text-xs text-slate-500 font-medium">
                <span className="flex items-center gap-2">
                  <Shield size={16} className="text-emerald-500" />
                  Active Models: DistilBERT ({CLASSIFIER_TEST_ACCURACY} accuracy), BERT-NER, MiniLM
                </span>
                <span className="text-slate-300">|</span>
                <span>{prompt.length} / {MAX_PROMPT_LENGTH}</span>
              </div>
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || !prompt.trim()}
                className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white text-sm font-semibold rounded-lg transition-colors"
              >
                {isAnalyzing ? <RefreshCw size={18} className="animate-spin" /> : <Send size={18} />}
                {isAnalyzing ? 'Analyzing...' : 'Scan Prompt'}
              </button>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center gap-3">
              <AlertCircle size={20} />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {results && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex-1 overflow-y-auto">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">
                Sanitized Payload
              </h3>
              <div className="bg-slate-900 rounded-lg p-5 font-mono text-sm leading-relaxed text-emerald-400 whitespace-pre-wrap">
                {results.processed_prompt}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Deep Telemetry Visualization */}
        <div className="lg:col-span-1 h-full overflow-y-auto">
          {results ? (
            <div className="space-y-6">
              <RiskGauge score={results.security_decision.risk_score} action={results.security_decision.action} />
              <ExplanationPanel results={results} />
            </div>
          ) : (
            <div className="bg-slate-50 border border-slate-200 border-dashed rounded-xl h-full flex flex-col items-center justify-center text-slate-400 p-8 text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm border border-slate-100 mb-4">
                <Zap size={24} className="text-indigo-500" />
              </div>
              <p className="font-medium text-slate-600">Ready to analyze</p>
              <p className="text-sm mt-2">Submit a prompt to view the risk score, policy action, detected entities, and full explanation.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
