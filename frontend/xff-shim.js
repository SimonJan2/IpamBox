// Overwrite X-Forwarded-For with the real socket peer on every request.
//
// The bundled Next standalone server only *fills* XFF when the header is
// absent — a client-supplied value would otherwise be proxied verbatim to
// the API, where it keys the login lockout counters (spoofable → bypass).
// This shim wraps http.createServer before server.js loads, so the rewrite
// proxy always forwards the actual peer address instead.
//
// Loaded via `node --require` in the Dockerfile CMD — keep it dependency-free.
"use strict";

const http = require("node:http");

const origCreateServer = http.createServer;
http.createServer = function patchedCreateServer(...args) {
  const server = origCreateServer.apply(this, args);
  // prepend so the header is fixed before Next's own request listener runs,
  // no matter how/where the app attaches it
  server.prependListener("request", (req) => {
    const peer = req.socket.remoteAddress || "";
    req.headers["x-forwarded-for"] = peer.replace(/^::ffff:/, "");
  });
  return server;
};
