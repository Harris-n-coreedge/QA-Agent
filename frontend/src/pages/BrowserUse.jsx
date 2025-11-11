import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Zap, Loader, CheckCircle, XCircle, Clock, Terminal, Globe, Brain, Activity, FileText, Code, Database, AlertCircle, CheckCircle2, X, MousePointerClick, Keyboard, ClipboardList } from 'lucide-react'
import { browserUseAPI } from '../api/client'

function BrowserUse() {
  const [task, setTask] = useState('')
  const [results, setResults] = useState([])
  const queryClient = useQueryClient()

  const executeMutation = useMutation({
    mutationFn: (taskDescription) => browserUseAPI.execute(taskDescription, 'google'),
    onSuccess: (data) => {
      setResults([{ ...data, id: Date.now() }, ...results])
      setTask('')
      // Invalidate test results query to refresh Dashboard and Test Results pages
      queryClient.invalidateQueries({ queryKey: ['test-results'] })
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (task.trim()) {
      executeMutation.mutate(task)
    }
  }

  const exampleTasks = [
    "We are going to check a test case, we will go to the website https://www.w3schools.com, click on sign button and login with the following credentials: username: abc@dd.com, password: 123 and then click again on sign in button and extract the error message and if error a message is displayed 'Invalid username or password' then test case is passed otherwise it is failed",
    "Verify navigation menu works correctly on https://github.com",
    "Check form validation on https://www.google.com search",
    "We are going to check a test case, we will go to the website https://wisemarket.com.pk, from left side menu click on 'Mobiles & Tablets' and then click on Mobile option, scroll down and click on 'Realme GT 7', click on its picture and then click on 'Add to Cart' button, click on 'View Cart' button and then click on 'Checkout' button, if a modal appears with a title 'Login to your wisemarket account' then test case is passed otherwise it is failed"
  ]
 
  return (
    <div className="layout-container space-y-10 fade-in">
      <div className="page-header">
        <h1 className="page-title">Browser Use</h1>
        <p className="page-description">
          Execute natural language tasks for browser automation
        </p>
      </div>

      <div className="glass-card p-5 md:p-6 hover-lift animate-fade-in" style={{ animationDelay: '0ms' }}>
        <div className="flex items-start gap-4 md:gap-6 mb-5 md:mb-6">
          <div className="p-3 md:p-4 rounded-xl bg-slate-700/50 border border-slate-600/50 flex-shrink-0">
            <Zap className="w-6 h-6 md:w-8 md:h-8 text-slate-300" />
          </div>
          <div className="min-w-0">
            <h2 className="text-xl md:text-2xl font-bold text-white mb-1 md:mb-2">
              Execute QA Test
            </h2>
            <p className="text-sm md:text-base text-slate-400">Describe the QA test case you want to execute</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 md:space-y-6">
          <div>
            <label className="label">QA Test Case Description</label>
            <textarea
              className="input min-h-[120px] md:min-h-[140px] text-sm md:text-base resize-none"
              placeholder="Describe the QA test case you want to execute (e.g., 'Test login functionality', 'Verify navigation menu', 'Check form validation')..."
              value={task}
              onChange={(e) => setTask(e.target.value)}
              disabled={executeMutation.isPending}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full text-sm md:text-base font-semibold"
            disabled={executeMutation.isPending || !task.trim()}
          >
            {executeMutation.isPending ? (
              <>
                <Loader className="w-6 h-6 animate-spin inline mr-3" />
                Executing QA Test...
              </>
            ) : (
              <>
                <Zap className="w-6 h-6 inline mr-3" />
                Execute QA Test
              </>
            )}
          </button>
        </form>

        {executeMutation.isError && (
          <div className="mt-8 bg-gradient-to-r from-red-500/25 to-red-500/15 text-red-100 p-6 rounded-2xl border border-red-500/40 backdrop-blur-xl shadow-2xl">
            <div className="flex items-start space-x-4">
              <XCircle className="w-6 h-6 flex-shrink-0 mt-1" />
              <div>
                <p className="font-bold text-lg">Error executing task</p>
                <p className="text-base mt-2">
                  {executeMutation.error.response?.data?.detail || executeMutation.error.message}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="glass-card p-5 md:p-6 hover-lift animate-fade-in" style={{ animationDelay: '100ms' }}>
        <div className="flex items-center gap-3 md:gap-4 mb-5 md:mb-6">
          <div className="p-2.5 md:p-3 rounded-lg bg-slate-700/50 border border-slate-600/50 flex-shrink-0">
            <Brain className="w-5 h-5 md:w-6 md:h-6 text-slate-300" />
          </div>
          <h3 className="text-lg md:text-xl font-bold text-white">
            Example QA Test Cases
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-5">
          {exampleTasks.map((example, idx) => (
            <button
              key={idx}
              style={{ animationDelay: `${(idx + 2) * 100}ms` }}
              className="text-left glass-card p-4 md:p-5 hover-lift group animate-slide-in-up transition-all duration-300 hover:scale-[1.02]"
              onClick={() => setTask(example)}
              disabled={executeMutation.isPending}
            >
              <p className="text-sm md:text-base text-slate-300 group-hover:text-white transition-colors leading-relaxed">
                {example}
              </p>
            </button>
          ))}
        </div>
      </div>

      {results.length > 0 && (
        <div className="space-y-6 md:space-y-8">
          <div className="text-center mb-6 md:mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-2 md:mb-3">
              Execution Results
            </h2>
            <p className="text-slate-400 text-sm md:text-base">Review your test execution outcomes</p>
          </div>
          {results.map((result, idx) => (
            <div key={result.id} style={{ animationDelay: `${idx * 0.1}s` }} className="card p-5 md:p-6 fade-in hover-lift">
              {/* Execution Header */}
              <div className="flex items-start gap-4 md:gap-6 mb-5 md:mb-6">
                <div className="p-3 md:p-4 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex-shrink-0">
                  <CheckCircle className="w-5 h-5 md:w-6 md:h-6 text-emerald-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-3 md:mb-4 flex-wrap gap-2">
                    <h3 className="text-lg md:text-xl font-semibold text-white">
                      Task Execution Completed
                    </h3>
                    <div className="flex items-center gap-2 flex-wrap">
                      {result.formatted_summary?.summary?.is_successful !== undefined && (
                        <span className={`badge flex items-center gap-1.5 ${
                          result.formatted_summary.summary.is_successful 
                            ? 'badge-success' 
                            : 'badge-error'
                        }`}>
                          {result.formatted_summary.summary.is_successful ? (
                            <>
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Success</span>
                            </>
                          ) : (
                            <>
                              <X className="w-3 h-3" />
                              <span>Failed</span>
                            </>
                          )}
                        </span>
                      )}
                      <span className="text-xs md:text-sm text-slate-400 font-mono px-3 py-1.5 rounded bg-slate-800/50 border border-slate-700/50">
                        {new Date(result.executed_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm md:text-base text-slate-300 mb-4 md:mb-5 italic bg-slate-800/50 p-4 md:p-5 rounded-lg border-l-4 border-slate-600/50">
                    "{result.task}"
                  </p>
                </div>
              </div>

              {/* Execution Details Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-5 md:mb-6">
                <div className="p-3 md:p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <p className="text-xs text-slate-400 mb-1.5 font-semibold uppercase tracking-wide">Execution Time</p>
                  <p className="text-sm md:text-base text-white font-mono font-semibold">
                    {new Date(result.executed_at).toLocaleTimeString()}
                  </p>
                </div>

                <div className="p-3 md:p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <p className="text-xs text-slate-400 mb-1.5 font-semibold uppercase tracking-wide">Status</p>
                  <p className="text-sm md:text-base text-white font-semibold">
                    {result.status || 'Completed'}
                  </p>
                </div>

                <div className="p-3 md:p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <p className="text-xs text-slate-400 mb-1.5 font-semibold uppercase tracking-wide">Execution Date</p>
                  <p className="text-xs md:text-sm text-white font-mono">
                    {new Date(result.executed_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="p-3 md:p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <p className="text-xs text-slate-400 mb-1.5 font-semibold uppercase tracking-wide">Provider</p>
                  <p className="text-sm md:text-base text-white font-semibold">
                    Google Gemini
                  </p>
                </div>
              </div>

              {/* Structured Summary */}
              {result.formatted_summary && (
              <div className="mb-5 md:mb-6">
                <h4 className="text-base md:text-lg font-semibold text-white mb-4 md:mb-5">
                    Execution Summary
                </h4>
                  <div className="bg-slate-800/50 backdrop-blur-xl p-5 md:p-6 rounded-xl border border-slate-700/50">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4 md:mb-5">
                      <div className="p-3 md:p-4 rounded-lg bg-slate-700/50 border border-slate-600/50">
                        <p className="text-xs text-slate-400 mb-1 font-semibold uppercase">Total Steps</p>
                        <p className="text-lg md:text-xl text-white font-bold">{result.formatted_summary.summary.total_steps}</p>
                      </div>
                      <div className="p-3 md:p-4 rounded-lg bg-slate-700/50 border border-slate-600/50">
                        <p className="text-xs text-slate-400 mb-1 font-semibold uppercase">URLs Visited</p>
                        <p className="text-lg md:text-xl text-white font-bold">{result.formatted_summary.summary.visited_urls_count}</p>
                      </div>
                      <div className={`p-3 md:p-4 rounded-lg border ${
                        result.formatted_summary.summary.has_errors 
                          ? 'bg-rose-500/10 border-rose-500/30' 
                          : 'bg-emerald-500/10 border-emerald-500/30'
                      }`}>
                        <p className={`text-xs mb-1 font-semibold uppercase ${
                          result.formatted_summary.summary.has_errors ? 'text-rose-300' : 'text-emerald-300'
                        }`}>Errors</p>
                        <p className={`text-lg md:text-xl font-bold ${
                          result.formatted_summary.summary.has_errors ? 'text-rose-200' : 'text-emerald-200'
                        }`}>
                          {result.formatted_summary.summary.has_errors ? 'Yes' : 'None'}
                        </p>
                      </div>
                      <div className={`p-3 md:p-4 rounded-lg border ${
                        result.formatted_summary.summary.is_successful 
                          ? 'bg-emerald-500/10 border-emerald-500/30' 
                          : 'bg-amber-500/10 border-amber-500/30'
                      }`}>
                        <p className={`text-xs mb-1 font-semibold uppercase ${
                          result.formatted_summary.summary.is_successful ? 'text-emerald-300' : 'text-amber-300'
                        }`}>Status</p>
                        <p className={`text-base md:text-lg font-bold ${
                          result.formatted_summary.summary.is_successful ? 'text-emerald-200' : 'text-amber-200'
                        }`}>
                          {result.formatted_summary.summary.is_done ? 'Done' : 'Running'}
                        </p>
                      </div>
                    </div>

                    {/* Visited URLs */}
                    {result.formatted_summary.visited_urls && result.formatted_summary.visited_urls.length > 0 && (
                      <div className="mb-6">
                        <h5 className="text-lg font-bold text-cyan-300 mb-3">Visited URLs</h5>
                        <div className="space-y-2">
                          {result.formatted_summary.visited_urls.map((url, idx) => (
                            <div key={idx} className="bg-black/30 p-3 rounded-lg border border-white/10">
                              <a href={url} target="_blank" rel="noopener noreferrer" 
                                className="text-cyan-300 hover:text-cyan-200 text-sm break-all underline">
                                {url}
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Actions Summary */}
                    {result.formatted_summary.actions_summary && result.formatted_summary.actions_summary.length > 0 && (
                      <div>
                        <h5 className="text-lg font-bold text-amber-300 mb-3">Actions Timeline</h5>
                        <div className="space-y-3 max-h-64 overflow-y-auto">
                          {result.formatted_summary.actions_summary.map((action, idx) => (
                            <div key={idx} className="bg-black/30 p-4 rounded-lg border border-white/10">
                              <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center space-x-3">
                                  <span className="text-amber-300 font-bold">Step {action.step}</span>
                                  <span className="text-blue-300 font-mono text-sm">{action.action_type}</span>
                                </div>
                                {action.success !== null && (
                                  <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded ${
                                    action.success 
                                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
                                      : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                  }`}>
                                    {action.success ? (
                                      <CheckCircle2 className="w-3 h-3" />
                                    ) : (
                                      <X className="w-3 h-3" />
                                    )}
                                  </span>
                                )}
                              </div>
                              {action.extracted_content && (
                                <p className="text-white text-sm italic ml-4">{action.extracted_content}</p>
                              )}
                              {action.error && (
                                <p className="text-red-300 text-sm ml-4 mt-1">{action.error}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* QA Test Results */}
              <div className="space-y-6">
                <h4 className="text-2xl font-bold text-gradient text-glow mb-6">
                  QA Test Results
                </h4>
                
                {/* Test Execution Summary */}
                <div className="bg-gradient-to-br from-white/10 to-white/5 p-8 rounded-3xl border border-white/15 shadow-xl">
                  <h4 className="text-lg font-bold text-emerald-300 mb-4">Test Execution Summary</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gradient-to-br from-emerald-500/15 to-green-500/10 p-6 rounded-2xl border border-emerald-500/30 shadow-xl">
                      <p className="text-emerald-300 text-sm mb-2 font-bold tracking-wide uppercase">Test Status</p>
                      <p className="text-emerald-200 font-black text-xl">{result.status}</p>
                    </div>
                    <div className="bg-gradient-to-br from-blue-500/15 to-indigo-500/10 p-6 rounded-2xl border border-blue-500/30 shadow-xl">
                      <p className="text-blue-300 text-sm mb-2 font-bold tracking-wide uppercase">Execution Time</p>
                      <p className="text-blue-200 font-black text-xl font-mono">
                        {new Date(result.executed_at).toLocaleTimeString()}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-500/15 to-violet-500/10 p-6 rounded-2xl border border-purple-500/30 shadow-xl">
                      <p className="text-purple-300 text-sm mb-2 font-bold tracking-wide uppercase">Test Date</p>
                      <p className="text-purple-200 font-black text-xl">
                        {new Date(result.executed_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Test Case Details */}
                <div className="bg-gradient-to-br from-white/10 to-white/5 p-8 rounded-3xl border border-white/15 shadow-xl">
                  <h4 className="text-lg font-bold text-blue-300 mb-4">Test Case Details</h4>
                  <div className="space-y-4">
                    <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                      <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">Test Description</p>
                      <p className="text-white font-bold text-lg">{result.task}</p>
                    </div>
                    
                    <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                      <p className="text-white/70 text-sm mb-4 font-bold tracking-wide uppercase">Test Results</p>
                      
                      {/* Parse and display structured terminal output */}
                      {(() => {
                        const terminalOutput = result.terminal_output || result.formatted_summary?.final_result || result.result || '';
                        
                        // Parse terminal output into structured format
                        const parseTerminalOutput = (output) => {
                          if (!output) return null;
                          
                          const lines = output.split('\n');
                          const parsed = {
                            steps: [],
                            summary: null,
                            testStatus: null,
                            finalResult: null,
                            sections: []
                          };
                          
                          let currentStep = null;
                          let currentSection = null;
                          let inSummary = false;
                          
                          for (let i = 0; i < lines.length; i++) {
                            const line = lines[i].trim();
                            
                            // Detect test status
                            if (line.includes('TEST CASE STATUS:') || line.includes('TEST CASE:')) {
                              if (line.includes('PASSED')) {
                                parsed.testStatus = { status: 'PASSED', color: 'green' };
                              } else if (line.includes('FAILED')) {
                                parsed.testStatus = { status: 'FAILED', color: 'red' };
                              } else if (line.includes('UNKNOWN')) {
                                parsed.testStatus = { status: 'UNKNOWN', color: 'yellow' };
                              }
                            }
                            
                            // Detect STEP headers
                            if (line.startsWith('STEP') && /STEP \d+/.test(line)) {
                              if (currentStep) parsed.steps.push(currentStep);
                              currentStep = {
                                number: line.match(/STEP (\d+)/)?.[1] || '',
                                action: '',
                                result: '',
                                status: null,
                                error: null,
                                positions: []
                              };
                            }
                            
                            // Detect section headers
                            if (line.includes('═════') || line.includes('─────')) {
                              if (line.includes('TEST SUMMARY') || line.includes('SUMMARY')) {
                                inSummary = true;
                              }
                            }
                            
                            // Parse step content
                            if (currentStep) {
                              if (line.startsWith('Action:')) {
                                currentStep.action = line.replace('Action:', '').trim();
                              } else if (line.startsWith('Result:') || line.startsWith('Extracted Information:')) {
                                currentStep.result = line.replace(/^(Result:|Extracted Information:)/, '').trim();
                              } else if (line.startsWith('Status:')) {
                                if (line.includes('SUCCESS')) {
                                  currentStep.status = 'success';
                                } else if (line.includes('FAILED')) {
                                  currentStep.status = 'failed';
                                }
                              } else if (line.startsWith('ERROR:') || line.startsWith('Error:')) {
                                currentStep.error = line.replace(/^(ERROR:|Error:)/, '').trim();
                              } else if (line.includes('Click Position:')) {
                                const pos = line.match(/\(([^)]+)\)/)?.[1];
                                if (pos) currentStep.positions.push({ type: 'click', pos });
                              } else if (line.includes('Input Position:')) {
                                const pos = line.match(/\(([^)]+)\)/)?.[1];
                                if (pos) currentStep.positions.push({ type: 'input', pos });
                              }
                            }
                            
                            // Detect final result
                            if (line.startsWith('Final Result:') && i < lines.length - 1) {
                              parsed.finalResult = lines.slice(i + 1).filter(l => l.trim()).join('\n');
                              break;
                            }
                          }
                          
                          if (currentStep) parsed.steps.push(currentStep);
                          
                          return parsed;
                        };
                        
                        const parsed = parseTerminalOutput(terminalOutput);
                        
                        if (parsed && parsed.steps.length > 0) {
                          // Show structured display
                          return (
                            <div className="space-y-4">
                              {/* Test Status Banner */}
                              {parsed.testStatus && (
                                <div className={`bg-gradient-to-r ${
                                  parsed.testStatus.color === 'green' ? 'from-green-500/25 to-emerald-500/15 border-green-500/40' :
                                  parsed.testStatus.color === 'red' ? 'from-red-500/25 to-rose-500/15 border-red-500/40' :
                                  'from-yellow-500/25 to-amber-500/15 border-yellow-500/40'
                                } p-4 rounded-xl border text-center`}>
                                  <div className="flex items-center justify-center gap-2">
                                    {parsed.testStatus.color === 'green' ? (
                                      <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                                    ) : parsed.testStatus.color === 'red' ? (
                                      <XCircle className="w-6 h-6 text-rose-400" />
                                    ) : (
                                      <AlertCircle className="w-6 h-6 text-amber-400" />
                                    )}
                                    <p className={`text-xl md:text-2xl font-bold ${
                                      parsed.testStatus.color === 'green' ? 'text-emerald-200' :
                                      parsed.testStatus.color === 'red' ? 'text-rose-200' :
                                      'text-amber-200'
                                    }`}>
                                      {parsed.testStatus.status}
                                    </p>
                                  </div>
                                </div>
                              )}
                              
                              {/* Steps Display */}
                              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                                {parsed.steps.map((step, idx) => (
                                  <div key={idx} className="bg-black/40 border border-white/10 rounded-lg p-4">
                                    <div className="flex items-center gap-3 mb-3">
                                      <span className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-lg font-bold text-sm">
                                        STEP {step.number}
                                      </span>
                                      {step.status && (
                                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs ${
                                          step.status === 'success' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                        }`}>
                                          {step.status === 'success' ? (
                                            <CheckCircle2 className="w-3 h-3" />
                                          ) : (
                                            <X className="w-3 h-3" />
                                          )}
                                        </span>
                                      )}
                                    </div>
                                    
                                    {step.action && (
                                      <div className="mb-2">
                                        <p className="text-blue-300 text-xs font-semibold mb-1">Action:</p>
                                        <p className="text-white/90 text-sm">{step.action}</p>
                                      </div>
                                    )}
                                    
                                    {step.result && (
                                      <div className="mb-2">
                                        <p className="text-cyan-300 text-xs font-semibold mb-1">Result:</p>
                                        <p className="text-white/80 text-sm whitespace-pre-wrap">{step.result}</p>
                                      </div>
                                    )}
                                    
                                    {step.positions.length > 0 && (
                                      <div className="mb-2">
                                        {step.positions.map((pos, pIdx) => (
                                          <div key={pIdx} className="flex items-center gap-1.5 text-slate-300 text-xs">
                                            {pos.type === 'click' ? (
                                              <MousePointerClick className="w-3.5 h-3.5 text-blue-400" />
                                            ) : (
                                              <Keyboard className="w-3.5 h-3.5 text-cyan-400" />
                                            )}
                                            <span className="font-medium">{pos.type === 'click' ? 'Click' : 'Input'} Position:</span>
                                            <span className="font-mono text-slate-400">({pos.pos})</span>
                                          </div>
                                        ))}
                                      </div>
                                    )}
                                    
                                    {step.error && (
                                      <div className="bg-red-500/20 border border-red-500/30 rounded p-2 mt-2">
                                        <div className="flex items-center gap-1.5 mb-1">
                                          <AlertCircle className="w-4 h-4 text-rose-400" />
                                          <p className="text-rose-300 text-xs font-semibold">Error:</p>
                                        </div>
                                        <p className="text-red-200 text-sm">{step.error}</p>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                              
                              {/* Final Result */}
                              {parsed.finalResult && (
                                <details className="bg-black/30 border border-white/10 rounded-lg p-4">
                                  <summary className="flex items-center gap-2 text-white/70 text-sm cursor-pointer hover:text-white font-semibold mb-2">
                                    <ClipboardList className="w-4 h-4 text-slate-400" />
                                    <span>Final Result Details</span>
                                  </summary>
                                  <pre className="text-white/80 text-xs mt-2 whitespace-pre-wrap font-mono">
                                    {parsed.finalResult}
                                  </pre>
                                </details>
                              )}
                              
                              {/* Raw Output (Collapsible) */}
                              <details className="bg-black/20 border border-white/10 rounded-lg p-4">
                                <summary className="text-white/60 text-xs cursor-pointer hover:text-white/80">
                                  View Raw Terminal Output
                                </summary>
                                <div className="bg-black p-4 rounded-lg mt-2 max-h-[300px] overflow-y-auto">
                                  <pre className="text-green-300 whitespace-pre-wrap leading-relaxed text-xs font-mono">
                                    {terminalOutput}
                                  </pre>
                                </div>
                              </details>
                            </div>
                          );
                        }
                        
                        // Fallback to raw display if parsing fails
                        return (
                          <div className="bg-gray-950 p-1 rounded-xl border border-gray-800 shadow-inner overflow-hidden">
                            <div className="bg-black p-4 rounded-lg max-h-[500px] overflow-y-scroll scrollbar-thin" style={{fontFamily: 'Consolas, "Courier New", monospace'}}>
                              <pre className="text-green-300 whitespace-pre-wrap leading-relaxed text-sm font-mono">
                                {terminalOutput || 'No output available'}
                              </pre>
                            </div>
                          </div>
                        );
                      })()}
                    </div>
                  </div>
                </div>

                {/* QA Metrics */}
                <div className="bg-gradient-to-br from-white/10 to-white/5 p-8 rounded-3xl border border-white/15 shadow-xl">
                  <h4 className="text-lg font-bold text-green-300 mb-4">QA Metrics</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Determine actual test outcome from terminal output */}
                    {(() => {
                      const terminalOutput = result.terminal_output || result.formatted_summary?.final_result || result.result || '';
                      // Prefer the explicit final summary markers; avoid false positives from earlier text
                      const passedMarker = /(\n|^)\s*✓\s*TEST CASE STATUS:\s*PASSED/i.test(terminalOutput) || /(\n|^)\s*TEST CASE:\s*PASSED/i.test(terminalOutput);
                      const failedMarker = /(\n|^)\s*✗\s*TEST CASE STATUS:\s*FAILED/i.test(terminalOutput) || /(\n|^)\s*TEST CASE:\s*FAILED/i.test(terminalOutput);
                      const heuristicPass = /test case is\s*\*\*passed\*\*|Test case is PASSED/i.test(terminalOutput);
                      const heuristicFail = /test case is\s*\*\*failed\*\*|Test case is FAILED/i.test(terminalOutput);

                      const isPassed = passedMarker || (!failedMarker && heuristicPass);
                      const isFailed = !isPassed && (failedMarker || heuristicFail);

                      const testOutcome = isPassed ? 'PASSED' : isFailed ? 'FAILED' : (result.status === 'completed' ? 'COMPLETED' : 'UNKNOWN');
                      const isTestPassed = isPassed;
                      
                      return (
                        <div className={`bg-gradient-to-br ${isTestPassed ? 'from-green-500/15 to-emerald-500/10 border-green-500/30' : isFailed ? 'from-red-500/15 to-rose-500/10 border-red-500/30' : 'from-yellow-500/15 to-amber-500/10 border-yellow-500/30'} p-6 rounded-2xl border shadow-xl`}>
                          <p className={`${isTestPassed ? 'text-green-300' : isFailed ? 'text-red-300' : 'text-yellow-300'} text-sm mb-2 font-bold tracking-wide uppercase`}>Test Outcome</p>
                          <p className={`${isTestPassed ? 'text-green-200' : isFailed ? 'text-red-200' : 'text-yellow-200'} font-black text-xl`}>
                            {testOutcome}
                          </p>
                        </div>
                      );
                    })()}
                    <div className="bg-gradient-to-br from-cyan-500/15 to-teal-500/10 p-6 rounded-2xl border border-cyan-500/30 shadow-xl">
                      <p className="text-cyan-300 text-sm mb-2 font-bold tracking-wide uppercase">Provider</p>
                      <p className="text-cyan-200 font-black text-xl">Google Gemini</p>
                    </div>
                  </div>
                </div>

                {/* Test Execution Log */}
                <div className="bg-gradient-to-br from-white/10 to-white/5 p-8 rounded-3xl border border-white/15 shadow-xl">
                  <h4 className="text-lg font-bold text-orange-300 mb-4">Test Execution Log</h4>
                  <div className="bg-black/50 p-6 rounded-2xl border border-white/10">
                    {(() => {
                      const terminalOutput = result.terminal_output || result.formatted_summary?.final_result || result.result || '';
                      const passedMarker = /(\n|^)\s*✓\s*TEST CASE STATUS:\s*PASSED/i.test(terminalOutput) || /(\n|^)\s*TEST CASE:\s*PASSED/i.test(terminalOutput);
                      const failedMarker = /(\n|^)\s*✗\s*TEST CASE STATUS:\s*FAILED/i.test(terminalOutput) || /(\n|^)\s*TEST CASE:\s*FAILED/i.test(terminalOutput);
                      const heuristicPass = /test case is\s*\*\*passed\*\*|Test case is PASSED/i.test(terminalOutput);
                      const heuristicFail = /test case is\s*\*\*failed\*\*|Test case is FAILED/i.test(terminalOutput);

                      const isPassed = passedMarker || (!failedMarker && heuristicPass);
                      const isFailed = !isPassed && (failedMarker || heuristicFail);

                      return (
                        <div className="space-y-3">
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                            <span className="text-green-300 font-mono text-sm">[INFO] Test case initialized</span>
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            <span className="text-blue-300 font-mono text-sm">[INFO] Executing test: {result.task}</span>
                          </div>
                          {isPassed && !isFailed ? (
                            <div className="flex items-center space-x-3">
                              <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                              <span className="text-emerald-300 font-mono text-sm">[SUCCESS] Test execution completed - PASSED</span>
                            </div>
                          ) : isFailed ? (
                            <div className="flex items-center space-x-3">
                              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                              <span className="text-red-300 font-mono text-sm">[FAILED] Test execution completed - FAILED</span>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-3">
                              <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                              <span className="text-emerald-300 font-mono text-sm">[INFO] Test execution completed</span>
                            </div>
                          )}
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                            <span className="text-purple-300 font-mono text-sm">[INFO] Results generated at {new Date(result.executed_at).toLocaleString()}</span>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && !executeMutation.isPending && (
        <div className="card text-center py-24 fade-in hover-lift">
          <div className="bg-gradient-to-br from-amber-500/15 to-yellow-500/10 w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-10 border border-amber-500/25 shadow-2xl">
            <Zap className="w-16 h-16 text-amber-300" />
          </div>
          <h3 className="text-6xl font-black text-gradient text-glow mb-8">
            No Results Yet
          </h3>
          <p className="text-white/80 text-2xl font-medium">Execute a task to see results here</p>
        </div>
      )}
    </div>
  )
}

export default BrowserUse
