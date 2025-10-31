import React, { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Zap, Loader, CheckCircle, XCircle, Clock, Terminal, Globe, Brain, Activity, FileText, Code, Database } from 'lucide-react'
import { browserUseAPI, testResultsAPI } from '../api/client'
import ApprovalPrompt from '../components/ApprovalPrompt'
import ResultVisualization from '../components/ResultVisualization'

function BrowserUse() {
  const [task, setTask] = useState('')
  const [latestResult, setLatestResult] = useState(null)
  const queryClient = useQueryClient()

  // Fetch test results from API (filter for browser automation tests)
  const { data: testResults, refetch: refetchResults } = useQuery({
    queryKey: ['browser-use-results'],
    queryFn: () => testResultsAPI.list(null, 50),
    refetchInterval: 3000,
  })

  // Filter only browser automation results
  const browserResults = testResults?.results?.filter(result =>
    result.command?.includes('Browser automation')
  ) || []

  // Combine latest result with fetched results, removing duplicates
  const allResults = React.useMemo(() => {
    const resultsMap = new Map()
    
    // Add latest result if it exists
    if (latestResult && latestResult.test_id) {
      resultsMap.set(latestResult.test_id, latestResult)
    }
    
    // Add all fetched results
    if (browserResults && Array.isArray(browserResults)) {
      browserResults.forEach(result => {
        if (result && result.test_id && !resultsMap.has(result.test_id)) {
          resultsMap.set(result.test_id, result)
        }
      })
    }
    
    // Return as sorted array (most recent first)
    return Array.from(resultsMap.values()).sort((a, b) => {
      const dateA = new Date(a.started_at || a.executed_at || a.completed_at || 0).getTime()
      const dateB = new Date(b.started_at || b.executed_at || b.completed_at || 0).getTime()
      return dateB - dateA
    })
  }, [latestResult, browserResults])

  const executeMutation = useMutation({
    mutationFn: (taskDescription) => browserUseAPI.execute(taskDescription, 'google'),
    onSuccess: (responseData) => {
      setTask('')
      
      // Create result object from response data immediately (show results right away)
      const resultFromResponse = {
        test_id: responseData.test_id || `temp-${Date.now()}`,
        session_id: null,
        command: `Browser automation: ${responseData.task}`,
        result: responseData.terminal_output || responseData.result || '',
        terminal_output: responseData.terminal_output || responseData.result || '',
        status: responseData.status || 'completed',
        started_at: responseData.executed_at || new Date().toISOString(),
        completed_at: responseData.executed_at || new Date().toISOString(),
        executed_at: responseData.executed_at || new Date().toISOString(),
        duration_ms: responseData.duration_ms || null
      }
      
      // Set result immediately so it shows up right away
      setLatestResult(resultFromResponse)
      
      // Also fetch the full result from the API if we have a test_id (may have more complete data)
      if (responseData.test_id) {
        // Try to fetch the full result, but don't wait - we already have data to display
        testResultsAPI.get(responseData.test_id)
          .then(result => {
            // Update with the full result from API (may have additional fields)
            setLatestResult({
              ...resultFromResponse,
              ...result,
              terminal_output: result.terminal_output || result.result || resultFromResponse.terminal_output,
              result: result.result || result.terminal_output || resultFromResponse.result
            })
            queryClient.invalidateQueries(['browser-use-results'])
            refetchResults()
          })
          .catch(() => {
            // If fetching fails, keep the result we already have
            queryClient.invalidateQueries(['browser-use-results'])
            refetchResults()
          })
      } else {
        // No test_id, just refetch all results
        queryClient.invalidateQueries(['browser-use-results'])
        refetchResults()
      }
    },
    onError: () => {
      // Clear latest result on error
      setLatestResult(null)
    }
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
    <div className="space-y-6 md:space-y-8 fade-in">
      <div className="slide-in text-center">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-gradient text-glow mb-3 tracking-tight">
          QA Test Automation
        </h1>
        <p className="text-white/70 text-sm md:text-base font-medium tracking-wide px-4">
          Automated QA testing with AI-powered test case execution
        </p>
      </div>

      <div className="card hover-lift">
        <div className="flex items-center space-x-3 md:space-x-4 mb-5">
          <div className="bg-gradient-to-br from-amber-500/25 to-yellow-500/15 p-3 rounded-2xl border border-amber-500/30 shadow-xl">
            <Zap className="w-6 h-6 md:w-7 md:h-7 text-amber-300" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg md:text-xl font-bold text-gradient text-glow">
              Execute QA Test
            </h2>
            <p className="text-xs md:text-sm text-white/60 font-medium hidden md:block">Describe the QA test case you want to execute</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 md:space-y-5">
          <div>
            <label className="label text-xs">QA Test Case Description</label>
            <textarea
              className="input min-h-[100px] md:min-h-[120px] text-sm md:text-base"
              placeholder="Describe the QA test case you want to execute (e.g., 'Test login functionality', 'Verify navigation menu', 'Check form validation')..."
              value={task}
              onChange={(e) => setTask(e.target.value)}
              disabled={executeMutation.isPending}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full text-sm md:text-base font-bold"
            disabled={executeMutation.isPending || !task.trim()}
          >
            {executeMutation.isPending ? (
              <>
                <Loader className="w-4 h-4 md:w-5 md:h-5 animate-spin inline mr-2" />
                Executing QA Test...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 md:w-5 md:h-5 inline mr-2" />
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
        <h3 className="text-lg md:text-xl font-bold text-gradient text-glow mb-5">
          Example QA Test Cases
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 md:gap-4">
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

      {allResults.length > 0 && (
        <div className="space-y-8">
          <h2 className="text-5xl font-black text-gradient text-glow text-center">
            Execution Results
          </h2>
          {allResults.map((result, idx) => (
            <div key={result.test_id || result.command + idx} style={{ animationDelay: `${idx * 0.15}s` }} className="card fade-in hover-lift">
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
                    <span className={`text-base font-bold px-3 py-1 rounded-lg ${
                      result.status === 'completed'
                        ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                        : 'bg-red-500/20 text-red-300 border border-red-500/30'
                    }`}>
                      {result.status === 'completed' ? '✓ Success' : '✗ Failed'}
                    </span>
                    <span className="text-base text-white/70 font-mono bg-gradient-to-r from-white/10 to-white/5 px-4 py-2 rounded-xl border border-white/20 shadow-lg">
                      {new Date(result.started_at || result.executed_at || result.completed_at || Date.now()).toLocaleString()}
                    </span>
                  </div>
                  </div>
                  <p className="text-white/90 mb-6 italic bg-gradient-to-r from-white/10 to-white/5 p-6 rounded-2xl border-l-4 border-amber-500/50 text-lg font-medium">
                    "{result.command?.replace('Browser automation: ', '')}"
                  </p>
                </div>
              </div>

              {/* Execution Details Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                  <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">Duration</p>
                  <p className="text-white font-bold text-lg font-mono">
                    {result.duration_ms ? `${(result.duration_ms / 1000).toFixed(2)}s` : 'N/A'}
                  </p>
                </div>

                <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                  <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">Status</p>
                  <p className="text-white font-bold text-lg capitalize">
                    {result.status}
                  </p>
                </div>

                <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                  <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">AI Provider</p>
                  <p className="text-white font-bold text-lg">
                    Google Gemini
                  </p>
                </div>
              </div>

              {/* Test Results */}
              <div className="bg-gradient-to-br from-white/10 to-white/5 p-8 rounded-3xl border border-white/15 shadow-xl">
                <h4 className="text-lg font-bold text-blue-300 mb-4">Test Results</h4>
                {result.terminal_output || result.result ? (
                  <ResultVisualization rawOutput={result.terminal_output || result.result} />
                ) : (
                  <div className="bg-black/30 p-4 rounded-xl border border-white/10">
                    <p className="text-white/60 text-sm">No output available yet. Results may still be processing...</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {allResults.length === 0 && !executeMutation.isPending && (
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

      {/* Confidence Scoring Approval Prompt */}
      <ApprovalPrompt />
    </div>
  )
}

export default BrowserUse
