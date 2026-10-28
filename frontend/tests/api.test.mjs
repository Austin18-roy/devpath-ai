import test from "node:test";
import assert from "node:assert/strict";

// Helper functions mirroring the logic in lib/api.ts for unit testing
function resolveApiBaseUrl(envUrl) {
  if (envUrl && envUrl.trim().length > 0) {
    return envUrl.replace(/\/+$/, "");
  }
  return "http://localhost:8000";
}

function validateHealthResponse(payload) {
  assert.equal(typeof payload, "object");
  assert.notEqual(payload, null);
  assert.equal(payload.status, "ok");
  assert.equal(payload.service, "devpath-ai-backend");
  assert.equal(typeof payload.version, "string");
  assert.equal(typeof payload.environment, "string");
  assert.equal(typeof payload.timestamp, "string");
  return true;
}

test("resolveApiBaseUrl returns default localhost:8000 when unset or empty", () => {
  assert.equal(resolveApiBaseUrl(undefined), "http://localhost:8000");
  assert.equal(resolveApiBaseUrl(""), "http://localhost:8000");
  assert.equal(resolveApiBaseUrl("   "), "http://localhost:8000");
});

test("resolveApiBaseUrl trims trailing slashes correctly", () => {
  assert.equal(resolveApiBaseUrl("http://localhost:8000/"), "http://localhost:8000");
  assert.equal(resolveApiBaseUrl("https://api.devpath.ai///"), "https://api.devpath.ai");
});

test("validateHealthResponse correctly validates healthy payload", () => {
  const samplePayload = {
    status: "ok",
    service: "devpath-ai-backend",
    version: "0.1.0",
    environment: "development",
    timestamp: "2026-10-28T08:30:00Z",
  };
  assert.equal(validateHealthResponse(samplePayload), true);
});

test("validateHealthResponse rejects invalid status", () => {
  const invalidPayload = {
    status: "error",
    service: "devpath-ai-backend",
  };
  assert.throws(() => validateHealthResponse(invalidPayload));
});

