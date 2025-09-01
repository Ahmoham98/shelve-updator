# 🧪 Basalam Shelves Updater - API Testing Suite

## 📋 Overview

This testing suite provides comprehensive testing for the Basalam Shelves Updater API. The suite includes multiple test files that cover different aspects of the application:

- **API Functionality Testing**
- **OAuth Flow Testing**
- **Performance & Load Testing**
- **Automated Test Runner**

## 🚀 Quick Start

### Prerequisites
1. **Server Running**: Ensure the application server is running
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Hosts Configuration**: Ensure `myapp.test` points to localhost
   ```bash
   # Add to C:\Windows\System32\drivers\etc\hosts
   127.0.0.1 myapp.test
   ```

### Run All Tests
```bash
python test_runner.py
```

## 📁 Test Files

### 1. `test_api_comprehensive.py` - Complete API Testing
Tests all API endpoints including:
- ✅ Server connectivity
- ✅ Authentication status
- ✅ Static file serving
- ✅ OAuth login redirect
- ✅ Protected endpoints
- ✅ User info endpoints
- ✅ Shelves API
- ✅ Product endpoints
- ✅ Update endpoints
- ✅ Error handling

### 2. `test_oauth_flow.py` - OAuth Flow Testing
Specifically tests OAuth implementation:
- ✅ OAuth URL generation
- ✅ Parameter validation
- ✅ State parameter handling
- ✅ Redirect URI configuration
- ✅ Callback endpoint structure

### 3. `test_performance.py` - Performance & Load Testing
Tests system performance:
- ✅ Static file response times
- ✅ API endpoint performance
- ✅ Concurrent request handling
- ✅ Cache effectiveness
- ✅ Load testing metrics

### 4. `test_runner.py` - Test Runner
Automates the testing process:
- ✅ Runs all test files
- ✅ Provides summary reports
- ✅ Checks server status
- ✅ Handles test failures gracefully

## 🎯 Test Categories

### 🔐 Authentication Tests
```bash
# Test auth status
curl http://127.0.0.1:8000/api/auth/status

# Test OAuth login
curl -I http://127.0.0.1:8000/auth/login
```

### 📊 API Endpoint Tests
```bash
# Health check
curl http://127.0.0.1:8000/api/health

# User info (requires auth)
curl http://127.0.0.1:8000/api/user/me

# Shelves list (requires auth)
curl http://127.0.0.1:8000/api/shelves

# Debug user info
curl http://127.0.0.1:8000/api/debug/user-info
```

### 🖼️ Static Files Tests
```bash
# Test static files with cache headers
curl -I http://127.0.0.1:8000/static/style.css
curl -I http://127.0.0.1:8000/static/app.js
curl -I http://127.0.0.1:8000/static/placeholder.jpg
```

### ⚡ Performance Tests
```bash
# Load test API endpoints
python test_performance.py

# Test concurrent requests
# (Included in performance test suite)
```

## 📊 Expected Test Results

### ✅ Successful Test Run
```
🧪 BASALAM SHELVES UPDATER - TEST SUITE
=======================================================================
✅ Server is running
✅ Auth status working
✅ Static files cached
✅ OAuth redirect working
✅ Protected endpoints secure
✅ User info endpoints working
✅ Shelves API working
✅ Update endpoints accessible

📊 TEST SUMMARY
Total Tests: 15
✅ Passed: 15
❌ Failed: 0
```

### 🔍 Individual Test Results

#### Static Files Test
```
✅ Static File: /static/style.css - Status: 200, Cache: public, max-age=86400
✅ Static File: /static/app.js - Status: 200, Cache: public, max-age=86400
✅ Static File: /static/placeholder.jpg - Status: 304, Cache: public, max-age=86400
```

#### OAuth Test
```
✅ OAuth Login Redirect - Redirect to: https://basalam.com/accounts/sso
✅ client_id: 1267
✅ scope: vendor.profile.read vendor.product.read customer.profile.read
✅ redirect_uri: http://myapp.test:8000/auth/callback
✅ state: [SECURE_STATE_TOKEN]
```

#### API Tests
```
✅ Health Endpoint - Status: healthy, Cached: true
✅ Auth Status - User is authenticated
✅ User Info (/api/user/me) - User ID: 18776979, Vendor ID: 1229542
✅ Shelves List - Found 3 shelves
✅ Shelf Products - Found 1 products
```

## 🔧 Troubleshooting

### ❌ Server Not Running
```bash
❌ Server not responding properly: 503

# Solution:
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### ❌ User Not Authenticated
```bash
❌ User is NOT authenticated

# Solution:
1. Open browser: http://myapp.test:8000
2. Click "ورود با بسلام" (Login with Basalam)
3. Complete OAuth flow
4. Re-run tests
```

### ❌ OAuth URL Issues
```bash
❌ Wrong redirect URL

# Solution:
Check .env file:
BASALAM_REDIRECT_URI=http://myapp.test:8000/auth/callback
```

### ❌ Static Files Not Cached
```bash
❌ Cache-Control: No cache header

# Solution:
Static file caching is implemented in main.py
Restart server to apply changes
```

### ❌ API Endpoints Failing
```bash
❌ Failed to get shelves: 422

# Solution:
Check backend logs for detailed error messages
Ensure user is authenticated and has vendor privileges
```

## 📈 Performance Benchmarks

### Static Files
- **Expected**: < 100ms response time
- **Cached**: < 50ms response time
- **Success Rate**: > 95%

### API Endpoints
- **Expected**: < 500ms response time
- **Success Rate**: > 95%

### Concurrent Requests
- **Expected**: Handle 10+ concurrent requests
- **Response Time**: < 2 seconds for 10 concurrent requests

## 🔄 Continuous Testing

### Automated Testing
```bash
# Run all tests
python test_runner.py

# Run specific test
python test_api_comprehensive.py
python test_oauth_flow.py
python test_performance.py
```

### Manual Testing Checklist
- [ ] Server starts without errors
- [ ] Home page loads (Persian RTL)
- [ ] OAuth login redirect works
- [ ] Authentication flow completes
- [ ] Dashboard shows shelves
- [ ] Static files load with cache headers
- [ ] API endpoints return expected data
- [ ] Error handling works properly
- [ ] Performance is acceptable

## 📋 Test Coverage

| Component | Tests | Status |
|-----------|-------|---------|
| Server Connectivity | Basic health checks | ✅ |
| Authentication | OAuth flow, token handling | ✅ |
| API Endpoints | All REST endpoints | ✅ |
| Static Files | Caching, error handling | ✅ |
| Performance | Load testing, concurrency | ✅ |
| Error Handling | Invalid requests, auth failures | ✅ |
| Security | State validation, CSRF protection | ✅ |

## 🎯 Testing Best Practices

1. **Always test with authentication** - Most endpoints require valid tokens
2. **Check server logs** - Detailed error messages are logged
3. **Test static file caching** - Verify cache headers are present
4. **Monitor performance** - Use performance tests to identify bottlenecks
5. **Test error scenarios** - Ensure proper error responses
6. **Validate OAuth flow** - Complete end-to-end OAuth testing

## 📞 Support

If tests are failing:

1. **Check server logs** for detailed error messages
2. **Verify environment configuration** in `.env`
3. **Ensure proper authentication** before testing protected endpoints
4. **Review test output** for specific failure details
5. **Check network connectivity** for external API calls

---

**🎉 The testing suite is now ready to thoroughly validate your Basalam Shelves Updater API!**
