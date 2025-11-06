import { FileDown, Download } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

export function usePDFExporter() {
  const toast = useToast()

  const generatePDF = (data, filename = 'test-report.pdf') => {
    try {
      // Create a new window for PDF generation
      const printWindow = window.open('', '_blank')
      
      if (!printWindow) {
        toast.error('Please allow popups to generate PDF')
        return
      }

      const htmlContent = `
        <!DOCTYPE html>
        <html>
          <head>
            <title>Test Report</title>
            <style>
              @media print {
                @page { margin: 1cm; }
                body { margin: 0; }
              }
              body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                padding: 20px;
                color: #0f172a;
                line-height: 1.6;
              }
              .header {
                border-bottom: 2px solid #334155;
                padding-bottom: 20px;
                margin-bottom: 30px;
              }
              .header h1 {
                margin: 0;
                color: #0f172a;
                font-size: 28px;
              }
              .header .meta {
                color: #64748b;
                margin-top: 10px;
                font-size: 14px;
              }
              .section {
                margin-bottom: 30px;
              }
              .section h2 {
                color: #1e293b;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 10px;
                margin-bottom: 15px;
              }
              .result-item {
                background: #f8fafc;
                border-left: 4px solid #3b82f6;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 4px;
              }
              .result-item.success {
                border-left-color: #10b981;
                background: #f0fdf4;
              }
              .result-item.error {
                border-left-color: #ef4444;
                background: #fef2f2;
              }
              .result-item.warning {
                border-left-color: #f59e0b;
                background: #fffbeb;
              }
              .result-title {
                font-weight: 600;
                margin-bottom: 8px;
                color: #0f172a;
              }
              .result-details {
                color: #475569;
                font-size: 14px;
              }
              table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
              }
              th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
              }
              th {
                background: #f1f5f9;
                font-weight: 600;
                color: #0f172a;
              }
              .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
              }
              .badge-success {
                background: #d1fae5;
                color: #065f46;
              }
              .badge-error {
                background: #fee2e2;
                color: #991b1b;
              }
              .badge-warning {
                background: #fef3c7;
                color: #92400e;
              }
              .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e2e8f0;
                text-align: center;
                color: #64748b;
                font-size: 12px;
              }
            </style>
          </head>
          <body>
            <div class="header">
              <h1>QA Test Report</h1>
              <div class="meta">
                Generated: ${new Date().toLocaleString()}<br>
                Website: ${data.websiteUrl || 'N/A'}<br>
                Test Type: ${data.testType || 'N/A'}
              </div>
            </div>

            ${data.summary ? `
              <div class="section">
                <h2>Summary</h2>
                <div class="result-item ${data.summary.status === 'passed' ? 'success' : data.summary.status === 'failed' ? 'error' : 'warning'}">
                  <div class="result-title">Overall Status: ${data.summary.status?.toUpperCase() || 'N/A'}</div>
                  ${data.summary.totalTests ? `<div class="result-details">Total Tests: ${data.summary.totalTests}</div>` : ''}
                  ${data.summary.passed ? `<div class="result-details">Passed: ${data.summary.passed}</div>` : ''}
                  ${data.summary.failed ? `<div class="result-details">Failed: ${data.summary.failed}</div>` : ''}
                </div>
              </div>
            ` : ''}

            ${data.performance ? `
              <div class="section">
                <h2>Performance Metrics</h2>
                <table>
                  <tr>
                    <th>Metric</th>
                    <th>Value</th>
                  </tr>
                  ${data.performance.loadTime ? `
                    <tr>
                      <td>Load Time</td>
                      <td>${data.performance.loadTime}ms</td>
                    </tr>
                  ` : ''}
                  ${data.performance.firstContentfulPaint ? `
                    <tr>
                      <td>First Contentful Paint</td>
                      <td>${data.performance.firstContentfulPaint}ms</td>
                    </tr>
                  ` : ''}
                  ${data.performance.networkRequests ? `
                    <tr>
                      <td>Network Requests</td>
                      <td>${data.performance.networkRequests}</td>
                    </tr>
                  ` : ''}
                </table>
              </div>
            ` : ''}

            ${data.results && data.results.length > 0 ? `
              <div class="section">
                <h2>Test Results</h2>
                ${data.results.map((result, index) => `
                  <div class="result-item ${result.status === 'passed' ? 'success' : result.status === 'failed' ? 'error' : 'warning'}">
                    <div class="result-title">${index + 1}. ${result.name || 'Test Case'}</div>
                    <div class="result-details">
                      <span class="badge badge-${result.status === 'passed' ? 'success' : result.status === 'failed' ? 'error' : 'warning'}">
                        ${result.status?.toUpperCase() || 'UNKNOWN'}
                      </span>
                      ${result.message ? `<p style="margin-top: 8px;">${result.message}</p>` : ''}
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : ''}

            ${data.recommendations && data.recommendations.length > 0 ? `
              <div class="section">
                <h2>Recommendations</h2>
                <ul>
                  ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
              </div>
            ` : ''}

            <div class="footer">
              <p>Report generated by QA Agent Platform</p>
              <p>© ${new Date().getFullYear()} QA Agent. All rights reserved.</p>
            </div>
          </body>
        </html>
      `

      printWindow.document.write(htmlContent)
      printWindow.document.close()
      
      // Wait for content to load, then print
      setTimeout(() => {
        printWindow.print()
        toast.success('PDF report generated successfully')
      }, 250)
    } catch (error) {
      toast.error(`Failed to generate PDF: ${error.message}`)
    }
  }

  const exportTestResult = (result) => {
    const reportData = {
      websiteUrl: result.website_url || result.url,
      testType: result.command || 'Unknown',
      summary: {
        status: result.status,
        totalTests: result.total_tests,
        passed: result.passed,
        failed: result.failed,
      },
      performance: result.performance_metrics || result.performance,
      results: result.test_results || result.results,
      recommendations: result.recommendations || [],
    }

    generatePDF(reportData, `test-report-${result.id || Date.now()}.pdf`)
  }

  return { generatePDF, exportTestResult }
}

export function PDFExportButton({ data, filename, className = '' }) {
  const { generatePDF } = usePDFExporter()

  return (
    <button
      onClick={() => generatePDF(data, filename)}
      className={`btn btn-secondary ${className}`}
    >
      <FileDown className="w-4 h-4" />
      <span>Export PDF</span>
    </button>
  )
}




