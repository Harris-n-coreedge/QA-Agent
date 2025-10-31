import { CheckCircle, XCircle, Globe, Smartphone, Zap, BarChart3 } from 'lucide-react';
import { parseTestResult, getBrowserInfo } from '../utils/resultParser';

// Cross-Browser Results Component
const CrossBrowserResults = ({ data }) => {
  if (!data?.browsers || data.browsers.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3 mb-5">
        <div className="bg-gradient-to-br from-blue-500/25 to-cyan-500/15 p-3 rounded-2xl border border-blue-500/30 shadow-xl">
          <Globe className="w-6 h-6 text-blue-300" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gradient text-glow">Cross-Browser Test Results</h3>
          <p className="text-xs text-white/60">Tested across {data.browsers.length} browsers</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.browsers.map((browser, idx) => {
          const browserInfo = getBrowserInfo(browser.name);
          return (
            <div
              key={idx}
              style={{ animationDelay: `${idx * 0.1}s` }}
              className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl p-5 rounded-2xl border border-white/15 hover:border-white/25 transition-all duration-300 hover:scale-105 group fade-in shadow-xl"
            >
              {/* Browser Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`bg-gradient-to-br ${browserInfo.color} p-2.5 rounded-xl border ${browserInfo.borderColor} shadow-lg`}>
                    <span className="text-2xl">{browserInfo.icon}</span>
                  </div>
                  <div>
                    <h4 className={`font-bold text-sm ${browserInfo.textColor}`}>{browserInfo.name}</h4>
                    <p className="text-xs text-white/50">Browser</p>
                  </div>
                </div>
                <div>
                  {browser.status === 'success' ? (
                    <CheckCircle className="w-6 h-6 text-green-400" />
                  ) : (
                    <XCircle className="w-6 h-6 text-red-400" />
                  )}
                </div>
              </div>

              {/* Page Title */}
              <div className="bg-gradient-to-r from-white/5 to-white/5 p-3 rounded-xl border border-white/10 mb-3">
                <p className="text-xs text-white/40 mb-1 uppercase font-semibold">Page Title</p>
                <p className="text-sm text-white/90 font-medium truncate">{browser.title}</p>
              </div>

              {/* Status Badge */}
              <div className={`inline-flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold ${
                browser.status === 'success'
                  ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                  : 'bg-red-500/20 text-red-300 border border-red-500/30'
              }`}>
                <span>{browser.status === 'success' ? '✓' : '✗'}</span>
                <span>{browser.status === 'success' ? 'Passed' : 'Failed'}</span>
              </div>

              {/* Screenshot indicator if available */}
              {browser.screenshot && (
                <div className="mt-3 text-xs text-white/50 flex items-center space-x-1">
                  <span>📸</span>
                  <span>Screenshot captured</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Auto Check Results Component
const AutoCheckResults = ({ data }) => {
  if (!data?.checks || data.checks.length === 0) return null;

  const categories = [
    { key: 'performance', label: 'Performance', icon: Zap, color: 'yellow' },
    { key: 'security', label: 'Security', icon: CheckCircle, color: 'green' },
    { key: 'accessibility', label: 'Accessibility', icon: Globe, color: 'blue' },
    { key: 'functional', label: 'Functional', icon: BarChart3, color: 'purple' }
  ];

  const getColorClasses = (color) => {
    const colors = {
      yellow: { bg: 'from-yellow-500/25 to-amber-500/15', border: 'border-yellow-500/30', text: 'text-yellow-300' },
      green: { bg: 'from-green-500/25 to-emerald-500/15', border: 'border-green-500/30', text: 'text-green-300' },
      blue: { bg: 'from-blue-500/25 to-cyan-500/15', border: 'border-blue-500/30', text: 'text-blue-300' },
      purple: { bg: 'from-purple-500/25 to-pink-500/15', border: 'border-purple-500/30', text: 'text-purple-300' }
    };
    return colors[color];
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3 mb-5">
        <div className="bg-gradient-to-br from-green-500/25 to-emerald-500/15 p-3 rounded-2xl border border-green-500/30 shadow-xl">
          <CheckCircle className="w-6 h-6 text-green-300" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gradient text-glow">Auto Check Results</h3>
          <p className="text-xs text-white/60">
            {data.checks.filter(c => c.status === 'passed').length} / {data.checks.length} checks passed
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map((category, idx) => {
          const checks = data.categorized[category.key] || [];
          if (checks.length === 0) return null;

          const Icon = category.icon;
          const colors = getColorClasses(category.color);

          return (
            <div
              key={category.key}
              style={{ animationDelay: `${idx * 0.1}s` }}
              className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl p-5 rounded-2xl border border-white/15 fade-in shadow-xl"
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className={`bg-gradient-to-br ${colors.bg} p-2 rounded-xl border ${colors.border}`}>
                  <Icon className={`w-5 h-5 ${colors.text}`} />
                </div>
                <h4 className={`font-bold text-sm ${colors.text}`}>{category.label}</h4>
              </div>

              <div className="space-y-2">
                {checks.map((check, checkIdx) => (
                  <div
                    key={checkIdx}
                    className="flex items-start space-x-2 bg-white/5 p-2.5 rounded-lg border border-white/10"
                  >
                    {check.status === 'passed' ? (
                      <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-white/90 font-medium">{check.name}</p>
                      {check.details && (
                        <p className="text-xs text-white/50 mt-1">{check.details}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Main Result Visualization Component
const ResultVisualization = ({ rawOutput }) => {
  if (!rawOutput) return null;

  const result = parseTestResult(rawOutput);

  if (!result) {
    return (
      <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15">
        <pre className="text-white/80 text-sm whitespace-pre-wrap font-mono">{rawOutput}</pre>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {result.type === 'cross-browser' && <CrossBrowserResults data={result.data} />}
      {result.type === 'auto-check' && <AutoCheckResults data={result.data} />}

      {/* Fallback to text display for unsupported types */}
      {(result.type === 'text' || result.type === 'unknown' || result.type === 'mobile' || result.type === 'auto-audit') && (
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl p-6 rounded-2xl border border-white/15 shadow-xl">
          <h3 className="text-lg font-bold text-gradient text-glow mb-4">Test Results</h3>
          <div className="bg-black/30 p-4 rounded-xl border border-white/10">
            <pre className="text-white/80 text-sm whitespace-pre-wrap font-mono leading-relaxed scrollbar-thin max-h-96 overflow-y-auto">
              {result.rawOutput}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultVisualization;
