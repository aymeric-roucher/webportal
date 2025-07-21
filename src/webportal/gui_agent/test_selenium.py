#!/usr/bin/env python3
"""
Capture network requests using Selenium with Firefox's DevTools
Works with standard selenium package (no selenium-wire needed)
"""

import argparse
import json
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class FirefoxNetworkMonitor:
    def __init__(self):
        self.driver = None

    def start(self):
        """Start Firefox with network capture enabled"""
        options = Options()

        # Enable devtools protocol
        options.set_preference("devtools.debugger.remote-enabled", True)
        options.set_preference("devtools.debugger.prompt-connection", False)

        # Create Firefox profile with network monitoring
        options.set_preference("devtools.netmonitor.persistlog", True)

        self.driver = webdriver.Firefox(options=options)
        print("Firefox started with network monitoring enabled")

    def inject_network_monitor(self):
        """Inject JavaScript to monitor network requests"""
        print("Injecting network monitoring script...")
        monitor_script = """
        // Create global storage for requests and console logs
        window.__networkRequests = [];
        window.__consoleErrors = [];
        window.__requestId = 0;
        
        // Store original fetch, XHR, and console methods
        const originalFetch = window.fetch;
        const originalXHR = window.XMLHttpRequest;
        const originalConsoleError = console.error;
        const originalConsoleWarn = console.warn;
        
        // Override console.error and console.warn to capture errors
        console.error = function(...args) {
            try {
                window.__consoleErrors.push({
                    type: 'error',
                    timestamp: new Date().toISOString(),
                    message: args.map(arg => {
                        try {
                            return typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
                        } catch(e) {
                            return String(arg);
                        }
                    }).join(' '),
                    stack: (new Error()).stack
                });
            } catch(e) {
                // Fallback if something goes wrong
                try {
                    window.__consoleErrors.push({
                        type: 'error',
                        timestamp: new Date().toISOString(),
                        message: 'Error capturing console.error: ' + String(e),
                        stack: null
                    });
                } catch(e2) {
                    // If even the fallback fails, just continue
                }
            }
            return originalConsoleError.apply(console, args);
        };
        
        console.warn = function(...args) {
            try {
                window.__consoleErrors.push({
                    type: 'warning',
                    timestamp: new Date().toISOString(),
                    message: args.map(arg => {
                        try {
                            return typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
                        } catch(e) {
                            return String(arg);
                        }
                    }).join(' '),
                    stack: (new Error()).stack
                });
            } catch(e) {
                // Fallback if something goes wrong
                try {
                    window.__consoleErrors.push({
                        type: 'warning',
                        timestamp: new Date().toISOString(),
                        message: 'Error capturing console.warn: ' + String(e),
                        stack: null
                    });
                } catch(e2) {
                    // If even the fallback fails, just continue
                }
            }
            return originalConsoleWarn.apply(console, args);
        };
        
        // Capture unhandled errors
        window.addEventListener('error', function(event) {
            window.__consoleErrors.push({
                type: 'uncaught_error',
                timestamp: new Date().toISOString(),
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                stack: event.error ? event.error.stack : null
            });
        });
        
        // Capture unhandled promise rejections
        window.addEventListener('unhandledrejection', function(event) {
            window.__consoleErrors.push({
                type: 'unhandled_rejection',
                timestamp: new Date().toISOString(),
                message: event.reason ? String(event.reason) : 'Unknown rejection',
                stack: event.reason && event.reason.stack ? event.reason.stack : null
            });
        });
        
        // Override fetch
        window.fetch = function(...args) {
            const requestId = ++window.__requestId;
            const url = args[0];
            const options = args[1] || {};
            const method = options.method || 'GET';
            const startTime = performance.now();
            
            const requestData = {
                id: requestId,
                type: 'fetch',
                url: url.toString(),
                method: method,
                headers: options.headers || {},
                body: options.body,
                timestamp: new Date().toISOString(),
                startTime: startTime
            };
            
            window.__networkRequests.push(requestData);
            
            return originalFetch.apply(window, args)
                .then(response => {
                    const clonedResponse = response.clone();
                    
                    // Capture response details
                    clonedResponse.text().then(body => {
                        const responseData = {
                            status: response.status,
                            statusText: response.statusText,
                            headers: {},
                            body: body, // Full response body as string
                            size: body.length,
                            duration: performance.now() - startTime
                        };
                        
                        // Capture headers
                        response.headers.forEach((value, key) => {
                            responseData.headers[key] = value;
                        });
                        
                        // Find and update request
                        const req = window.__networkRequests.find(r => r.id === requestId);
                        if (req) {
                            req.response = responseData;
                            req.completed = true;
                        }
                    }).catch(err => {
                        console.error('Error reading response:', err);
                    });
                    
                    return response;
                })
                .catch(error => {
                    const req = window.__networkRequests.find(r => r.id === requestId);
                    if (req) {
                        req.error = error.message;
                        req.completed = true;
                        req.duration = performance.now() - startTime;
                    }
                    throw error;
                });
        };
        
        // Override XMLHttpRequest
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const requestId = ++window.__requestId;
            let method, url, startTime;
            
            const originalOpen = xhr.open;
            const originalSend = xhr.send;
            const originalSetRequestHeader = xhr.setRequestHeader;
            
            const headers = {};
            
            xhr.open = function(...args) {
                method = args[0];
                url = args[1];
                return originalOpen.apply(this, args);
            };
            
            xhr.setRequestHeader = function(header, value) {
                headers[header] = value;
                return originalSetRequestHeader.apply(this, arguments);
            };
            
            xhr.send = function(body) {
                startTime = performance.now();
                
                const requestData = {
                    id: requestId,
                    type: 'xhr',
                    url: url,
                    method: method,
                    headers: headers,
                    body: body,
                    timestamp: new Date().toISOString(),
                    startTime: startTime
                };
                
                window.__networkRequests.push(requestData);
                
                xhr.addEventListener('load', function() {
                    const responseData = {
                        status: xhr.status,
                        statusText: xhr.statusText,
                        headers: xhr.getAllResponseHeaders(),
                        body: xhr.responseText, // Full response body
                        size: xhr.responseText.length,
                        duration: performance.now() - startTime
                    };
                    
                    const req = window.__networkRequests.find(r => r.id === requestId);
                    if (req) {
                        req.response = responseData;
                        req.completed = true;
                    }
                });
                
                xhr.addEventListener('error', function() {
                    const req = window.__networkRequests.find(r => r.id === requestId);
                    if (req) {
                        req.error = 'Network error';
                        req.completed = true;
                        req.duration = performance.now() - startTime;
                    }
                });
                
                return originalSend.apply(this, arguments);
            };
            
            return xhr;
        };
        
        // Helper functions accessible from Selenium
        window.getNetworkRequests = function() {
            return window.__networkRequests;
        };
        
        window.clearNetworkRequests = function() {
            window.__networkRequests = [];
        };
        
        window.getConsoleErrors = function() {
            return window.__consoleErrors;
        };
        
        window.clearConsoleErrors = function() {
            window.__consoleErrors = [];
        };
        
        window.getRequestsSummary = function() {
            const requests = window.__networkRequests;
            const summary = {
                total: requests.length,
                completed: requests.filter(r => r.completed).length,
                failed: requests.filter(r => r.error).length,
                byType: {
                    fetch: requests.filter(r => r.type === 'fetch').length,
                    xhr: requests.filter(r => r.type === 'xhr').length
                },
                byMethod: {}
            };
            
            requests.forEach(req => {
                summary.byMethod[req.method] = (summary.byMethod[req.method] || 0) + 1;
            });
            
            return summary;
        };
        
        console.log('Network monitoring injected. Use getNetworkRequests() to retrieve data.');
        
        // Test that monitoring is working
        window.__monitoringActive = true;
        """

        self.driver.execute_script(monitor_script)
        print("Network monitoring script injected")

    def navigate(self, url):
        """Navigate to a URL"""
        print(f"Navigating to: {url}")
        # First navigate to about:blank and inject the monitor
        self.driver.get("about:blank")
        self.inject_network_monitor()
        
        # Now navigate to the actual URL
        self.driver.get(url)
        time.sleep(1)  # Brief delay to ensure page is ready
        # Re-inject monitor to ensure it's active on the target page
        self.inject_network_monitor()

    def get_requests(self):
        """Get all captured requests from the browser"""
        try:
            # Check if monitoring is active
            monitoring_active = self.driver.execute_script("return window.__monitoringActive;")
            if not monitoring_active:
                print("Warning: Network monitoring is not active")
                return []
            
            requests = self.driver.execute_script("return window.getNetworkRequests();")
            print(f"Retrieved {len(requests or [])} requests from browser")
            return requests or []
        except Exception as e:
            print(f"Error getting requests: {e}")
            return []

    def get_summary(self):
        """Get summary of network requests"""
        try:
            return self.driver.execute_script("return window.getRequestsSummary();")
        except:
            return None

    def clear_requests(self):
        """Clear all captured requests"""
        self.driver.execute_script("window.clearNetworkRequests();")

    def get_console_errors(self):
        """Get all captured console errors"""
        try:
            # First check if the function exists
            function_exists = self.driver.execute_script("return typeof window.getConsoleErrors === 'function';")
            if not function_exists:
                print("Warning: getConsoleErrors function not found. Re-injecting script...")
                self.inject_network_monitor()
                
            # Check if the console errors array exists
            array_exists = self.driver.execute_script("return Array.isArray(window.__consoleErrors);")
            if not array_exists:
                print("Warning: __consoleErrors array not found")
                return []
            
            errors = self.driver.execute_script("return window.getConsoleErrors();")
            print(f"Retrieved {len(errors or [])} console errors from browser")
            return errors or []
        except Exception as e:
            print(f"Error getting console errors: {e}")
            return []

    def clear_console_errors(self):
        """Clear all captured console errors"""
        self.driver.execute_script("window.clearConsoleErrors();")

    def wait(self, seconds):
        """Wait for a specified time"""
        print(f"Waiting {seconds} seconds...")
        time.sleep(seconds)

    def export_requests(self, filename="network_requests.json"):
        """Export captured requests and console errors to JSON file"""
        requests = self.get_requests()
        console_errors = self.get_console_errors()

        data = {
            "captureTime": datetime.now().isoformat(),
            "url": self.driver.current_url,
            "title": self.driver.title,
            "requestCount": len(requests),
            "consoleErrorCount": len(console_errors),
            "requests": requests,
            "consoleErrors": console_errors,
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Exported {len(requests)} requests and {len(console_errors)} console errors to {filename}")

    def print_summary(self):
        """Print summary of captured requests"""
        summary = self.get_summary()
        requests = self.get_requests()

        if summary:
            print("\n=== Network Request Summary ===")
            print(f"Total requests: {summary['total']}")
            print(f"Completed: {summary['completed']}")
            print(f"Failed: {summary['failed']}")

            print("\nBy Type:")
            for type_name, count in summary["byType"].items():
                print(f"  {type_name}: {count}")

            print("\nBy Method:")
            for method, count in summary["byMethod"].items():
                print(f"  {method}: {count}")

        # Additional analysis
        if requests:
            domains = {}
            total_size = 0

            for req in requests:
                # Extract domain
                try:
                    if "://" in req["url"]:
                        domain = req["url"].split("://")[1].split("/")[0]
                        domains[domain] = domains.get(domain, 0) + 1
                except:
                    pass

                # Calculate sizes
                if req.get("response") and req["response"].get("size"):
                    total_size += req["response"]["size"]

            print("\nTop domains:")
            for domain, count in sorted(
                domains.items(), key=lambda x: x[1], reverse=True
            )[:10]:
                print(f"  {domain}: {count}")

            print(
                f"\nTotal response size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)"
            )

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()


def main():
    parser = argparse.ArgumentParser(description="Capture Firefox network requests")
    parser.add_argument("url", help="URL to visit")
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Capture duration in seconds",
    )
    parser.add_argument(
        "--output", default="network_requests.json", help="Output JSON filename"
    )

    args = parser.parse_args()

    monitor = FirefoxNetworkMonitor()

    try:
        monitor.start()
        monitor.navigate(args.url)

        print(f"Capturing network traffic for {args.duration} seconds...")
        print("You can interact with the browser during this time")

        monitor.wait(args.duration)

        monitor.print_summary()
        monitor.export_requests(args.output)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        monitor.close()


if __name__ == "__main__":
    main()
