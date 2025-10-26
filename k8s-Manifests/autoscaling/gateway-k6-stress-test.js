/*
Performance testing script for the gateway service
import http from 'k6/http';
import { check } from 'k6';

// --- CONFIGURATION ---
// This placeholder URL assumes you are running k6 INSIDE your EKS cluster
// and targeting a service named 'gateway-service' in the 'default' namespace
// on port 8081.

// Set your target endpoint here. For in-cluster test, use service DNS. For external, use the public URL.
const TARGET_URL = 'http://gateway-service:8081/health'; // Change if needed

export let options = {
    // This executor runs a fixed number of VUs for a fixed duration.
    executor: 'constant-vus',
    vus: 50,       // A low, normal number of users
    duration: '5m',  // Run for 5 minutes

    thresholds: {
        // This test defines our "baseline" success.
        // We expect it to be 100% successful and very fast.
        'http_req_failed': ['rate < 0.01'], // Fail if more than 1% of requests fail
        'http_req_duration{expected_response:true}': ['p(95) < 100'], // p(95) response time must be < 100ms
    },
};

// --- TEST LOGIC ---
export default function () {
    let res = http.get(TARGET_URL);

    check(res, {
        'status is 2xx': (r) => r.status >= 200 && r.status < 300,
    });
}
*/

import http from "k6/http";
import { check } from "k6";

// --- CONFIGURATION ---
const TARGET_URL = "http://gateway-service:8081/health";

export let options = {
  scenarios: {
    stress_breakpoint: {
      executor: "constant-vus",
      vus: 5000,
      duration: "5m",
      gracefulStop: "30s",
    },
  },
  thresholds: {
    // Alert if error rate exceeds 10% (bottleneck/failure point)
    http_req_failed: ["rate < 0.1"],
    // Optional: Alert if 95th percentile latency exceeds 1s
    http_req_duration: ["p(95)<1000"],
  },
};

// --- TEST LOGIC ---

export default function () {
  let res = http.get(TARGET_URL);
  check(res, {
    "status is 2xx": (r) => r.status >= 200 && r.status < 300,
  });
  // Optionally, add more checks or log errors for analysis
}
