import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

/**
 * ApprovalPrompt Component - Fixed infinite loop issue
 */
const ApprovalPrompt = () => {
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [currentApproval, setCurrentApproval] = useState(null);
  const [responding, setResponding] = useState(false);
  const [debugInfo, setDebugInfo] = useState('Initializing...');
  const [fetchCount, setFetchCount] = useState(0);

  // Use ref to store apiClient (doesn't cause re-renders)
  const apiClientRef = useRef(null);
  const isInitialized = useRef(false);

  // Initialize API client ONCE
  useEffect(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    console.log('🔧 ApprovalPrompt: Initializing...');

    const initClient = async () => {
      // Try proxy first
      const proxyClient = axios.create({
        baseURL: '/api/v1',
        headers: { 'Content-Type': 'application/json' },
        timeout: 3000
      });

      try {
        console.log('🔧 Testing proxy connection...');
        await proxyClient.get('/approvals/pending');
        console.log('✅ Connected via proxy');
        apiClientRef.current = proxyClient;
        setDebugInfo('Connected via proxy');
      } catch (proxyErr) {
        console.log('❌ Proxy failed:', proxyErr.message);
        // Try direct connection
        const directClient = axios.create({
          baseURL: 'http://localhost:8000/api/v1',
          headers: { 'Content-Type': 'application/json' },
          timeout: 3000
        });

        try {
          console.log('🔧 Testing direct connection...');
          await directClient.get('/approvals/pending');
          console.log('✅ Connected directly');
          apiClientRef.current = directClient;
          setDebugInfo('Connected directly');
        } catch (directErr) {
          console.error('❌ Cannot connect to backend');
          console.error('Direct error:', directErr.message);
          setDebugInfo('Backend offline');
        }
      }
    };

    initClient();
  }, []); // Empty deps - run once

  // Poll for approvals - runs independently
  useEffect(() => {
    console.log('🔧 Poll effect triggered, apiClient:', !!apiClientRef.current);

    if (!apiClientRef.current) {
      console.log('⏸️ Polling not started - waiting for API client');
      // Try again after a short delay
      const retry = setTimeout(() => {
        if (apiClientRef.current) {
          console.log('✅ API client ready, will start polling on next render');
        }
      }, 1000);
      return () => clearTimeout(retry);
    }

    console.log('▶️ Starting approval polling (every 2s)');
    let pollCount = 0;

    const fetchApprovals = async () => {
      try {
        pollCount++;
        console.log(`📡 Poll #${pollCount}: Fetching approvals...`);

        const response = await apiClientRef.current.get('/approvals/pending');
        const approvals = response.data;

        console.log(`📊 Poll #${pollCount}: Found ${approvals.length} approvals`, approvals);

        setFetchCount(pollCount);
        setDebugInfo(`${approvals.length} pending`);
        setPendingApprovals(approvals);

        // Update approval if we found one
        if (approvals.length > 0) {
          console.log('🔔 NEW APPROVAL DETECTED - Setting modal:', approvals[0].request_id);
          setCurrentApproval(approvals[0]);
        } else {
          console.log('📭 No approvals found');
          setCurrentApproval(null);
        }
      } catch (err) {
        console.error('❌ Poll error:', err.message);
        setDebugInfo('Poll error');
      }
    };

    // Start immediately
    fetchApprovals();

    // Then poll every 2 seconds
    const interval = setInterval(fetchApprovals, 2000);

    return () => {
      console.log('⏹️ Stopping approval polling');
      clearInterval(interval);
    };
  }, [apiClientRef.current]); // Re-run when API client is ready

  // Handle response
  const handleResponse = async (approved) => {
    if (!currentApproval || responding || !apiClientRef.current) return;

    console.log(`📤 ${approved ? 'APPROVING ✅' : 'DENYING ❌'}`);
    setResponding(true);

    try {
      await apiClientRef.current.post('/approvals/respond', {
        request_id: currentApproval.request_id,
        approved: approved,
        user_notes: null
      });

      console.log(`✅ SUCCESS! ${approved ? 'Task executing' : 'Task cancelled'}`);

      setCurrentApproval(null);
      setPendingApprovals([]);

    } catch (err) {
      console.error('❌ Response failed:', err);
      alert(`Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setResponding(false);
    }
  };

  const getTimeRemaining = (expiresAt) => {
    return Math.max(0, Math.floor((new Date(expiresAt) - new Date()) / 1000));
  };

  const getBadgeColor = (level) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-300',
      risky: 'bg-orange-100 text-orange-800 border-orange-300',
      low: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      medium: 'bg-blue-100 text-blue-800 border-blue-300',
      high: 'bg-green-100 text-green-800 border-green-300'
    };
    return colors[level] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const debugIndicator = (
    <div className="fixed bottom-4 right-4 z-40 bg-blue-600 text-white px-3 py-2 rounded-lg text-xs font-mono shadow-lg">
      🛡️ {debugInfo} | Polls: {fetchCount} | Current: {currentApproval ? 'YES' : 'NO'}
    </div>
  );

  // ALWAYS render debug indicator
  console.log('🎨 Rendering ApprovalPrompt - currentApproval:', currentApproval);

  if (!currentApproval) {
    console.log('⏸️ No approval - showing debug only');
    return debugIndicator;
  }

  console.log('🚨 SHOWING MODAL for approval:', currentApproval.request_id);
  const timeRemaining = getTimeRemaining(currentApproval.expires_at);

  return (
    <>
      {debugIndicator}
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm">
        <div className="bg-white rounded-lg shadow-2xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-auto">

          <div className="bg-gradient-to-r from-orange-500 to-red-600 p-6">
            <div className="flex items-center gap-4 text-white">
              <div className="text-5xl">⚠️</div>
              <div className="flex-1">
                <h2 className="text-3xl font-bold">Approval Required</h2>
                <p className="text-orange-100 text-sm mt-1">Risky operation detected</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">{timeRemaining}s</div>
                <div className="text-xs text-orange-100">remaining</div>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            <div className="flex justify-center">
              <span className={`px-6 py-3 rounded-full text-base font-bold border-2 ${getBadgeColor(currentApproval.confidence_level)}`}>
                {currentApproval.confidence_level.toUpperCase()} Risk
                <span className="ml-2">({Math.round(currentApproval.confidence_score * 100)}%)</span>
              </span>
            </div>

            <div className="bg-gray-50 p-5 rounded-lg border-l-4 border-orange-500">
              <h3 className="text-sm font-semibold text-gray-700 mb-2 uppercase">Task:</h3>
              <p className="text-base font-medium text-gray-900">{currentApproval.action_description}</p>
            </div>

            <div className="bg-blue-50 p-5 rounded-lg border border-blue-200">
              <h3 className="text-sm font-semibold text-blue-900 mb-2 uppercase">Why?</h3>
              <p className="text-sm text-blue-800">{currentApproval.reasoning}</p>
            </div>

            {currentApproval.risk_factors?.length > 0 && (
              <div className="bg-orange-50 p-5 rounded-lg border border-orange-200">
                <h3 className="text-sm font-semibold text-orange-900 mb-3 uppercase flex items-center gap-2">
                  <span>⚠️</span> Risk Factors:
                </h3>
                <ul className="space-y-2">
                  {currentApproval.risk_factors.map((factor, i) => (
                    <li key={i} className="flex gap-3 text-sm text-orange-900">
                      <span className="text-orange-500 font-bold">•</span>
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="bg-gray-100 p-6 flex gap-4 rounded-b-lg">
            <button
              onClick={() => handleResponse(false)}
              disabled={responding}
              className="flex-1 flex items-center justify-center gap-3 px-6 py-4 bg-red-600 text-white rounded-lg text-lg font-bold hover:bg-red-700 disabled:opacity-50 transition-all shadow-lg"
            >
              <span className="text-2xl">✕</span>
              <span>DENY</span>
            </button>

            <button
              onClick={() => handleResponse(true)}
              disabled={responding}
              className="flex-1 flex items-center justify-center gap-3 px-6 py-4 bg-green-600 text-white rounded-lg text-lg font-bold hover:bg-green-700 disabled:opacity-50 transition-all shadow-lg"
            >
              <span className="text-2xl">✓</span>
              <span>APPROVE</span>
            </button>
          </div>

          {responding && (
            <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center rounded-lg">
              <div className="text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-orange-500 mx-auto"></div>
                <p className="mt-4 text-lg font-semibold text-gray-700">Sending...</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ApprovalPrompt;
