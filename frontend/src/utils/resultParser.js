/**
 * Professional Test Result Parser
 * Transforms raw test output into beautiful, structured data
 */

export const parseTestResult = (rawOutput) => {
  if (!rawOutput) return null;

  const result = {
    type: 'unknown',
    data: null,
    rawOutput
  };

  // Parse Cross-Browser Test Results
  if (rawOutput.includes('Cross-browser test results:')) {
    result.type = 'cross-browser';
    result.data = parseCrossBrowserResults(rawOutput);
    return result;
  }

  // Parse Mobile Test Results
  if (rawOutput.includes('Mobile test completed') || rawOutput.includes('Screenshots captured')) {
    result.type = 'mobile';
    result.data = parseMobileResults(rawOutput);
    return result;
  }

  // Parse Auto Check Results
  if (rawOutput.includes('Auto check completed') || rawOutput.includes('✅ Load test') || rawOutput.includes('Performance check')) {
    result.type = 'auto-check';
    result.data = parseAutoCheckResults(rawOutput);
    return result;
  }

  // Parse Auto Audit Results
  if (rawOutput.includes('Auto audit completed') || rawOutput.includes('SEO') || rawOutput.includes('Link health')) {
    result.type = 'auto-audit';
    result.data = parseAutoAuditResults(rawOutput);
    return result;
  }

  // Default: just structured text
  result.type = 'text';
  result.data = { text: rawOutput };
  return result;
};

// Parse Cross-Browser Test Results
const parseCrossBrowserResults = (output) => {
  const browsers = [];
  const lines = output.split('\n');

  const browserRegex = /^\s*(chromium|firefox|webkit|chrome|safari|edge):\s*(✅|✓|❌|✗)\s*(.+)$/i;

  lines.forEach(line => {
    const match = line.match(browserRegex);
    if (match) {
      const [, browser, status, details] = match;

      // Extract title
      const titleMatch = details.match(/Title:\s*(.+?)(?:\.\.\.|$)/);
      const title = titleMatch ? titleMatch[1].trim() : '';

      // Extract screenshot
      const screenshotMatch = details.match(/Screenshot:\s*([^\s]+)/);
      const screenshot = screenshotMatch ? screenshotMatch[1].trim() : null;

      // Extract URL
      const urlMatch = details.match(/URL:\s*([^\s]+)/);
      const url = urlMatch ? urlMatch[1].trim() : null;

      browsers.push({
        name: browser.toLowerCase(),
        status: (status === '✅' || status === '✓') ? 'success' : 'failed',
        title: title || 'Page loaded successfully',
        screenshot,
        url,
        details: details.replace(/Title:.*?(?:\.\.\.|$)/, '').replace(/Screenshot:.*?(?:\s|$)/, '').trim()
      });
    }
  });

  return { browsers };
};

// Parse Mobile Test Results
const parseMobileResults = (output) => {
  const data = {
    device: 'Mobile Device',
    screenshots: [],
    status: 'success'
  };

  // Extract device name
  const deviceMatch = output.match(/Device:\s*([^\n]+)/i);
  if (deviceMatch) {
    data.device = deviceMatch[1].trim();
  }

  // Extract viewport dimensions
  const viewportMatch = output.match(/(\d+)\s*x\s*(\d+)/);
  if (viewportMatch) {
    data.viewport = {
      width: parseInt(viewportMatch[1]),
      height: parseInt(viewportMatch[2])
    };
  }

  // Extract screenshot count
  const screenshotMatch = output.match(/(\d+)\s*screenshots?/i);
  if (screenshotMatch) {
    data.screenshotCount = parseInt(screenshotMatch[1]);
  }

  return data;
};

// Parse Auto Check Results
const parseAutoCheckResults = (output) => {
  const checks = [];
  const lines = output.split('\n');

  const checkRegex = /^\s*(✅|✓|❌|✗)\s*(.+?)(?::|$)/;

  lines.forEach(line => {
    const match = line.match(checkRegex);
    if (match) {
      const [, status, name] = match;
      const details = line.split(':')[1]?.trim() || '';

      checks.push({
        name: name.trim(),
        status: (status === '✅' || status === '✓') ? 'passed' : 'failed',
        details
      });
    }
  });

  // Categorize checks
  const categorized = {
    performance: checks.filter(c => /performance|load|speed|time/i.test(c.name)),
    security: checks.filter(c => /security|header|ssl|https/i.test(c.name)),
    accessibility: checks.filter(c => /accessibility|a11y|aria/i.test(c.name)),
    functional: checks.filter(c => !/performance|security|accessibility/i.test(c.name))
  };

  return { checks, categorized };
};

// Parse Auto Audit Results
const parseAutoAuditResults = (output) => {
  const audits = {
    seo: [],
    performance: [],
    accessibility: [],
    issues: [],
    recommendations: []
  };

  const lines = output.split('\n');
  let currentSection = null;

  lines.forEach(line => {
    // Detect section headers
    if (/SEO/i.test(line)) currentSection = 'seo';
    else if (/Performance/i.test(line)) currentSection = 'performance';
    else if (/Accessibility/i.test(line)) currentSection = 'accessibility';
    else if (/Issue|Problem|Error/i.test(line)) currentSection = 'issues';
    else if (/Recommend|Suggest|Fix/i.test(line)) currentSection = 'recommendations';

    // Parse items
    const itemMatch = line.match(/^\s*[•\-*]\s*(.+)/);
    if (itemMatch && currentSection) {
      audits[currentSection].push(itemMatch[1].trim());
    }
  });

  return audits;
};

// Get browser icon and color
export const getBrowserInfo = (browserName) => {
  const browsers = {
    chromium: {
      name: 'Chromium',
      icon: '🌐',
      color: 'from-blue-500/25 to-cyan-500/15',
      borderColor: 'border-blue-500/30',
      textColor: 'text-blue-300'
    },
    chrome: {
      name: 'Chrome',
      icon: '🌐',
      color: 'from-blue-500/25 to-cyan-500/15',
      borderColor: 'border-blue-500/30',
      textColor: 'text-blue-300'
    },
    firefox: {
      name: 'Firefox',
      icon: '🦊',
      color: 'from-orange-500/25 to-red-500/15',
      borderColor: 'border-orange-500/30',
      textColor: 'text-orange-300'
    },
    webkit: {
      name: 'WebKit',
      icon: '🧭',
      color: 'from-purple-500/25 to-pink-500/15',
      borderColor: 'border-purple-500/30',
      textColor: 'text-purple-300'
    },
    safari: {
      name: 'Safari',
      icon: '🧭',
      color: 'from-purple-500/25 to-pink-500/15',
      borderColor: 'border-purple-500/30',
      textColor: 'text-purple-300'
    },
    edge: {
      name: 'Edge',
      icon: '🌊',
      color: 'from-teal-500/25 to-cyan-500/15',
      borderColor: 'border-teal-500/30',
      textColor: 'text-teal-300'
    }
  };

  return browsers[browserName?.toLowerCase()] || browsers.chromium;
};
