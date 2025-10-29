import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Zap, Loader, CheckCircle, XCircle, Clock, Terminal, Globe, Brain, Activity, FileText, Code, Database } from 'lucide-react'
import { browserUseAPI } from '../api/client'

function BrowserUse() {
  const [task, setTask] = useState('')
  const [results, setResults] = useState([])

  const executeMutation = useMutation({
    mutationFn: (taskDescription) => browserUseAPI.execute(taskDescription, 'google'),
    onSuccess: (data) => {
      setResults([{ ...data, id: Date.now() }, ...results])
      setTask('')
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
    <div className="space-y-12 fade-in">
      <div className="slide-in text-center">
        <h1 className="text-8xl font-black text-gradient text-glow mb-8 tracking-tight">
          QA Test Automation
        </h1>
        <p className="text-white/80 text-2xl font-medium tracking-wide">Automated QA testing with AI-powered test case execution</p>
      </div>

      <div className="card hover-lift">
        <div className="flex items-center space-x-6 mb-10">
          <div className="bg-gradient-to-br from-amber-500/25 to-yellow-500/15 p-6 rounded-3xl border border-amber-500/30 shadow-2xl">
            <Zap className="w-12 h-12 text-amber-300" />
          </div>
          <div>
            <h2 className="text-4xl font-bold text-gradient text-glow">
              Execute QA Test
            </h2>
            <p className="text-lg text-white/70 font-medium">Describe the QA test case you want to execute</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          <div>
            <label className="label">QA Test Case Description</label>
            <textarea
              className="input min-h-[120px] text-lg"
              placeholder="Describe the QA test case you want to execute (e.g., 'Test login functionality', 'Verify navigation menu', 'Check form validation')..."
              value={task}
              onChange={(e) => setTask(e.target.value)}
              disabled={executeMutation.isPending}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full text-xl font-bold"
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

      <div className="card hover-lift">
        <h3 className="text-3xl font-bold text-gradient text-glow mb-10">
          Example QA Test Cases
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {exampleTasks.map((example, idx) => (
            <button
              key={idx}
              style={{ animationDelay: `${idx * 0.15}s` }}
              className="text-left bg-gradient-to-br from-white/10 to-white/5 hover:from-white/15 hover:to-white/10 p-8 rounded-3xl transition-all duration-700 transform hover:scale-[1.03] hover:-translate-y-2 border border-white/15 hover:border-white/25 group fade-in shadow-xl hover:shadow-2xl"
              onClick={() => setTask(example)}
              disabled={executeMutation.isPending}
            >
              <p className="text-base text-white/80 group-hover:text-white transition-colors leading-relaxed font-medium">
                {example}
              </p>
            </button>
          ))}
        </div>
      </div>

      {results.length > 0 && (
        <div className="space-y-8">
          <h2 className="text-5xl font-black text-gradient text-glow text-center">
            Execution Results
          </h2>
          {results.map((result, idx) => (
            <div key={result.id} style={{ animationDelay: `${idx * 0.15}s` }} className="card fade-in hover-lift">
              {/* Execution Header */}
              <div className="flex items-start space-x-6 mb-8">
                <div className="bg-gradient-to-br from-emerald-500/25 to-green-500/15 p-4 rounded-2xl border border-emerald-500/30 shadow-2xl">
                  <CheckCircle className="w-8 h-8 text-emerald-300 flex-shrink-0" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-3xl font-bold text-gradient text-glow">
                      Task Execution Completed
                    </h3>
                  <div className="flex items-center space-x-2">
                    {result.formatted_summary?.summary?.is_successful !== undefined && (
                      <span className={`text-base font-bold px-3 py-1 rounded-lg ${
                        result.formatted_summary.summary.is_successful 
                          ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                          : 'bg-red-500/20 text-red-300 border border-red-500/30'
                      }`}>
                        {result.formatted_summary.summary.is_successful ? '✓ Success' : '✗ Failed'}
                      </span>
                    )}
                    <span className="text-base text-white/70 font-mono bg-gradient-to-r from-white/10 to-white/5 px-4 py-2 rounded-xl border border-white/20 shadow-lg">
                      {new Date(result.executed_at).toLocaleString()}
                    </span>
                  </div>
                  </div>
                  <p className="text-white/90 mb-6 italic bg-gradient-to-r from-white/10 to-white/5 p-6 rounded-2xl border-l-4 border-amber-500/50 text-lg font-medium">
                    "{result.task}"
                  </p>
                </div>
              </div>

              {/* Execution Details Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                  <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">Execution Time</p>
                  <p className="text-white font-bold text-lg font-mono">
                    {new Date(result.executed_at).toLocaleTimeString()}
                  </p>
                </div>

                <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                  <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">Status</p>
                  <p className="text-white font-bold text-lg">
                    {result.status || 'Completed'}
                  </p>
                </div>

                <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                  <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">Execution Date</p>
                  <p className="text-white font-mono text-sm">
                    {new Date(result.executed_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                  <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">AI Provider</p>
                  <p className="text-white font-bold text-lg">
                    Google Gemini
                  </p>
                </div>
              </div>

              {/* Structured Summary */}
              {result.formatted_summary && (
              <div className="mb-8">
                <h4 className="text-2xl font-bold text-gradient text-glow mb-6">
                    Execution Summary
                </h4>
                  <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-2xl p-8 rounded-3xl border border-white/15 shadow-xl">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                      <div className="bg-gradient-to-br from-purple-500/15 to-violet-500/10 p-4 rounded-2xl border border-purple-500/30">
                        <p className="text-purple-300 text-xs mb-1 font-bold uppercase">Total Steps</p>
                        <p className="text-purple-200 font-black text-2xl">{result.formatted_summary.summary.total_steps}</p>
                      </div>
                      <div className="bg-gradient-to-br from-blue-500/15 to-indigo-500/10 p-4 rounded-2xl border border-blue-500/30">
                        <p className="text-blue-300 text-xs mb-1 font-bold uppercase">URLs Visited</p>
                        <p className="text-blue-200 font-black text-2xl">{result.formatted_summary.summary.visited_urls_count}</p>
                      </div>
                      <div className={`p-4 rounded-2xl border ${
                        result.formatted_summary.summary.has_errors 
                          ? 'bg-gradient-to-br from-red-500/15 to-rose-500/10 border-red-500/30' 
                          : 'bg-gradient-to-br from-green-500/15 to-emerald-500/10 border-green-500/30'
                      }`}>
                        <p className={`text-xs mb-1 font-bold uppercase ${
                          result.formatted_summary.summary.has_errors ? 'text-red-300' : 'text-green-300'
                        }`}>Errors</p>
                        <p className={`font-black text-2xl ${
                          result.formatted_summary.summary.has_errors ? 'text-red-200' : 'text-green-200'
                        }`}>
                          {result.formatted_summary.summary.has_errors ? 'Yes' : 'None'}
                        </p>
                      </div>
                      <div className={`p-4 rounded-2xl border ${
                        result.formatted_summary.summary.is_successful 
                          ? 'bg-gradient-to-br from-green-500/15 to-emerald-500/10 border-green-500/30' 
                          : 'bg-gradient-to-br from-yellow-500/15 to-orange-500/10 border-yellow-500/30'
                      }`}>
                        <p className={`text-xs mb-1 font-bold uppercase ${
                          result.formatted_summary.summary.is_successful ? 'text-green-300' : 'text-yellow-300'
                        }`}>Status</p>
                        <p className={`font-black text-lg ${
                          result.formatted_summary.summary.is_successful ? 'text-green-200' : 'text-yellow-200'
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
                                  <span className={`text-xs px-2 py-1 rounded ${
                                    action.success 
                                      ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                                      : 'bg-red-500/20 text-red-300 border border-red-500/30'
                                  }`}>
                                    {action.success ? '✓' : '✗'}
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
                      <div className="bg-gray-950 p-1 rounded-xl border border-gray-800 shadow-inner overflow-hidden">
                        <div className="bg-black p-4 rounded-lg max-h-[500px] overflow-y-scroll scrollbar-thin" style={{fontFamily: 'Consolas, "Courier New", monospace'}}>
                          <pre className="text-green-300 whitespace-pre-wrap leading-relaxed text-sm font-mono">
                            {result.terminal_output || result.formatted_summary?.final_result || result.result || 'No output available'}
                        </pre>
                        </div>
                      </div>
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
                      <p className="text-cyan-300 text-sm mb-2 font-bold tracking-wide uppercase">AI Provider</p>
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
