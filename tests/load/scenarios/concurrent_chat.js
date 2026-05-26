import http from 'k6/http';
import { check, sleep } from 'k6';

// k6 config options for load testing scenarios
export const options = {
  stages: [
    { duration: '30s', target: 50 },  // Ramp-up to 50 concurrent virtual users (VUs)
    { duration: '1m', target: 100 },   // Maintain 100 VUs (simulating active parallel chat loads)
    { duration: '30s', target: 0 },   // Ramp-down to 0
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],    // Error rate must be less than 1% (stability)
    http_req_duration: ['p(95)<500'],  // 95% of request durations should be under 500ms (latency SLA)
  },
};

const BASE_URL = 'http://localhost:8000/api/v1';

export default function () {
  // 1. Generate unique mock customer details
  const senderId = `load_test_customer_${__VU}_${__ITER}`;
  
  // 2. Perform message routing delivery
  const payload = JSON.stringify({
    tenant_id: 'tenant-test-default-uuid',
    channel: 'web',
    sender_id: senderId,
    content: 'Halo, saya ingin menanyakan jam operasional toko hari ini.',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'mock-hiqonis-api-key-value-for-testing',
    },
  };

  // POST route message to the API conversation endpoint
  const res = http.post(`${BASE_URL}/conversations/route`, payload, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'reply generated successfully': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.status === 'ai_handled' || body.status === 'human_takeover';
      } catch (e) {
        return false;
      }
    },
  });

  // Simulate thinking delay between customer replies (1 to 3 seconds)
  sleep(Math.random() * 2 + 1);
}
