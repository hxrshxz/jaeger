
#### /home/hxrshxz/Desktop/Projects/jaeger/cmd/jaeger/internal/extension/jaegerquery/internal/apiv3/http_gateway.go
- Action: REPLACE
- Logic: "Replace the fallback logic for the `limit` and `num_traces` parameters. The current implementation incorrectly uses `num_traces` when `limit=0` is explicitly provided. The fix involves checking for the *presence* of the `limit` parameter in the query string, rather than checking its parsed value."
  ```go
  	// The 'limit' parameter is preferred over the deprecated 'num_traces'.
  	_, limitIsPresent := q[paramLimit]
  	if limitIsPresent {
  		limitStr := q.Get(paramLimit)
  		limit, err := strconv.Atoi(limitStr)
  		if h.tryParamError(w, err, paramLimit) {
  			return nil, true
  		}
  		queryParams.SearchDepth = limit
  	} else {
  		// Fallback to 'num_traces' if 'limit' was not provided.
  		if numTracesStr := q.Get(paramNumTraces); numTracesStr != "" {
  			if numTraces, err := strconv.Atoi(numTracesStr); err == nil {
  				queryParams.SearchDepth = numTraces
  			} else if h.tryParamError(w, err, paramNumTraces) {
  				return nil, true
  			}
  		}
  	}

  	return queryParams, false
  ```
- Verification: "The existing tests, once fixed, will validate this change. Specifically, the new test case for `limit=0` will ensure the fallback to `num_traces` does not occur."

#### /home/hxrshxz/Desktop/Projects/jaeger/cmd/jaeger/internal/extension/jaegerquery/internal/apiv3/http_gateway_test.go
- Action: REPLACE
- Logic: "Refactor the `TestHTTPGatewayFindTracesLimitAndNumTraces` test to prevent state pollution between table-driven test cases. The `baseQuery` map was being reused, causing modifications in one test to affect others. The fix is to create a new, clean `url.Values` map for each test case. Additionally, a new test case is added to validate the behavior of the `limit=0` edge case."
  ```go
  func TestHTTPGatewayFindTracesLimitAndNumTraces(t *testing.T) {
  	time1 := time.Now().UTC().Truncate(time.Nanosecond)
  	time2 := time1.Add(-time.Second).UTC().Truncate(time.Nanosecond)

  	baseQuery := func() url.Values {
  		q := url.Values{}
  		q.Set(paramServiceName, "test-service")
  		q.Set(paramTimeMin, time1.Format(time.RFC3339Nano))
  		q.Set(paramTimeMax, time2.Format(time.RFC3339Nano))
  		return q
  	}

  	baseExpectedParams := func() tracestore.TraceQueryParams {
  		return tracestore.TraceQueryParams{
  			ServiceName:  "test-service",
  			Attributes:   pcommon.NewMap(),
  			StartTimeMin: time1,
  			StartTimeMax: time2,
  		}
  	}

  	testCases := []struct {
  		name           string
  		query          url.Values
  		expectedParams tracestore.TraceQueryParams
  		expectedStatus int
  		expectedError  string
  	}{
  		{
  			name: "should use num_traces when limit is not present",
  			query: func() url.Values {
  				q := baseQuery()
  				q.Set(paramNumTraces, "75")
  				return q
  			}(),
  			expectedParams: func() tracestore.TraceQueryParams {
  				p := baseExpectedParams()
  				p.SearchDepth = 75
  				return p
  			}(),
  			expectedStatus: http.StatusOK,
  		},
  		{
  			name: "should use limit when both limit and num_traces are present",
  			query: func() url.Values {
  				q := baseQuery()
  				q.Set(paramLimit, "50")
  				q.Set(paramNumTraces, "75")
  				return q
  			}(),
  			expectedParams: func() tracestore.TraceQueryParams {
  				p := baseExpectedParams()
  				p.SearchDepth = 50
  				return p
  			}(),
  			expectedStatus: http.StatusOK,
  		},
  		{
  			name: "should use limit=0 and ignore num_traces",
  			query: func() url.Values {
  				q := baseQuery()
  				q.Set(paramLimit, "0")
  				q.Set(paramNumTraces, "75")
  				return q
  			}(),
  			expectedParams: func() tracestore.TraceQueryParams {
  				p := baseExpectedParams()
  				p.SearchDepth = 0
  				return p
  			}(),
  			expectedStatus: http.StatusOK,
  		},
  		{
  			name: "should return error for invalid num_traces",
  			query: func() url.Values {
  				q := baseQuery()
  				q.Set(paramNumTraces, "invalid")
  				return q
  			}(),
  			expectedStatus: http.StatusBadRequest,
  			expectedError:  "malformed parameter query.num_traces",
  		},
  	}

  	for _, tc := range testCases {
  		t.Run(tc.name, func(t *testing.T) {
  			gw := setupHTTPGatewayNoServer(t, "")
  			if tc.expectedStatus == http.StatusOK {
  				gw.reader.
  					On("FindTraces", matchContext, tc.expectedParams).
  					Return(iter.Seq2[[]ptrace.Traces, error](func(yield func([]ptrace.Traces, error) bool) {
  						yield([]ptrace.Traces{makeTestTrace()}, nil)
  					})).Once()
  			}

  			r, err := http.NewRequest(http.MethodGet, "/api/v3/traces?"+tc.query.Encode(), http.NoBody)
  			require.NoError(t, err)
  			w := httptest.NewRecorder()
  			gw.router.ServeHTTP(w, r)

  			assert.Equal(t, tc.expectedStatus, w.Code)
  			if tc.expectedError != "" {
  				assert.Contains(t, w.Body.String(), tc.expectedError)
  			}
  			gw.reader.AssertExpectations(t)
  		})
  	}
  }
  ```
- Verification: "Run the Go tests for this package. All tests, including the new `limit=0` case, should pass, confirming both the test isolation and the correctness of the application logic."

#### /home/hxrshxz/Desktop/Projects/jaeger/FIX_PLAN.md
- Action: DELETE
- Logic: "Remove the temporary development artifact `FIX_PLAN.md` from the project."
- Verification: "Confirm the file has been deleted from the filesystem."
