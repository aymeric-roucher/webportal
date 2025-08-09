# Anti-Detection Stealth Features

This document outlines the comprehensive stealth features implemented to bypass bot detection systems when crawling websites.

## 🎯 Overview

The stealth system implements multiple layers of defense against common bot detection techniques used by websites:

1. **Browser Fingerprint Masking**
2. **User Agent & Header Rotation** 
3. **Behavioral Simulation**
4. **Proxy Support**
5. **JavaScript Environment Manipulation**

## 🚀 Features Implemented

### 1. Selenium Agent Stealth (`selenium_agent.py`)

**Browser Configuration:**
- Removes automation indicators (`--disable-blink-features=AutomationControlled`)
- Disables automation extensions
- Randomizes window dimensions
- Comprehensive Chrome argument stealth profile

**JavaScript Injection:**
- Overrides `navigator.webdriver` property
- Masks automation-specific browser properties
- Simulates realistic hardware characteristics
- Removes webdriver traces from navigator prototype

**Behavioral Simulation:**
- Human-like click patterns with coordinate randomization
- Realistic typing delays between keystrokes
- Random pre/post-action delays
- Curved mouse movements

### 2. Playwright Crawler Stealth (`crawl.py`)

**Request Headers:**
- Rotates realistic user agents from multiple browsers/OS
- Comprehensive HTTP header profiles
- Randomized Accept-Language headers
- Proper Sec-Fetch-* headers for modern browsers

**Browser Arguments:**
- Extended list of stealth-focused Chrome arguments
- Disables telemetry, background processes, and fingerprinting vectors
- Removes automation control features

**JavaScript Masking:**
- Injects stealth scripts on page initialization
- Overrides automation detection properties
- Masks timezone fingerprinting
- Simulates realistic browser environment

### 3. Crawl4AI Enhancement (`crawl4ai_tools.py`)

**Configuration:**
- Stealth-focused browser configuration
- Random delays before crawling
- Comprehensive header profiles
- JavaScript automation masking

### 4. Proxy Management (`proxy_manager.py`)

**Proxy Rotation:**
- Fetches free proxies from multiple sources
- Tests proxy reliability before use
- Automatic proxy rotation and refresh
- Fallback to direct connection if proxies fail

**Integration:**
- Environment variable controlled (`USE_PROXY=true`)
- Works with both Selenium and Playwright
- Handles proxy failures gracefully

## 🛠 Usage

### Environment Variables

```bash
# Enable stealth features
export USE_STEALTH=true

# Enable proxy rotation (optional)
export USE_PROXY=true

# Enable random delays
export STEALTH_RANDOM_DELAYS=true
```

### Docker Deployment

The Docker image includes all necessary dependencies and environment variables:

```dockerfile
ENV USE_STEALTH=true
ENV USE_PROXY=false  # Set to true if you want proxy rotation
ENV STEALTH_RANDOM_DELAYS=true
```

### Testing Stealth Features

Run the comprehensive stealth test:

```bash
python src/webportal/stealth/test_stealth.py
```

This will test:
- Selenium stealth configuration
- Playwright stealth setup
- Request header profiles
- Proxy manager functionality

## 🔧 Technical Details

### Browser Arguments Applied

```bash
--disable-blink-features=AutomationControlled
--disable-features=VizDisplayCompositor,VizServiceDisplay
--disable-ipc-flooding-protection
--disable-backgrounding-occluded-windows
--disable-renderer-backgrounding
--disable-background-networking
--disable-extensions
--disable-plugins
--disable-logging
--no-sandbox
--disable-dev-shm-usage
```

### JavaScript Overrides

```javascript
// Remove webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
});

// Simulate realistic browser environment
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
});

// Add Chrome runtime object
window.chrome = { runtime: {} };

// Override hardware fingerprinting
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 4,
});
```

### User Agent Rotation

The system rotates between realistic user agents:
- Windows 10 Chrome 120
- macOS Chrome 120  
- Windows Chrome 119
- Linux Chrome 120

### Behavioral Patterns

**Human-like Clicking:**
- ±2 pixel coordinate randomization
- Curved mouse movements
- 0.1-0.5s pre-click delays
- 0.1-0.3s post-click delays

**Realistic Typing:**
- 20-150ms delays between keystrokes
- Occasional longer pauses (200-800ms) 
- Character-by-character typing

## 🚨 Detection Bypass Techniques

### Common Detection Methods Addressed:

1. **WebDriver Property Detection** ✅
   - JavaScript property masking
   - Prototype chain cleaning

2. **Browser Automation Flags** ✅
   - Comprehensive Chrome argument profile
   - Automation extension disabling

3. **User Agent Analysis** ✅  
   - Realistic UA rotation
   - Matching header profiles

4. **Behavioral Analysis** ✅
   - Human-like interaction patterns
   - Randomized timing delays

5. **Fingerprinting** ✅
   - Hardware property simulation
   - Screen resolution randomization

6. **Network Patterns** ✅
   - Request header normalization
   - Optional proxy rotation

## 📊 Effectiveness

The implemented stealth features successfully bypass:
- Basic webdriver detection
- User agent filtering
- Simple behavioral analysis
- Header-based bot detection
- Common fingerprinting techniques

### Test Sites Passed:
- bot.sannysoft.com
- Cloudflare bot detection  
- Basic rate limiting systems

## 🔄 Continuous Improvement

**Monitoring:** Regularly test against new detection methods

**Updates:** Keep user agents and browser versions current

**Proxy Sources:** Maintain reliable proxy sources for rotation

**Behavioral Patterns:** Enhance human simulation algorithms

## ⚠️ Important Notes

- Stealth features may impact crawling speed due to added delays
- Proxy rotation can cause intermittent failures
- Always respect website terms of service and robots.txt
- Some advanced detection systems may still identify automation
- Use responsibly and for legitimate research purposes only

## 🤝 Contributing

When adding new stealth features:
1. Test against common detection sites
2. Document new techniques in this file  
3. Ensure backward compatibility
4. Add environment variable controls
5. Update Docker configuration as needed