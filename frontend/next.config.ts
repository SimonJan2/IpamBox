import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Articles prerender at build time so their markdown is baked into the HTML;
  // this keeps the source files traced into the standalone bundle as a safety
  // net if the docs routes ever become dynamic.
  outputFileTracingIncludes: {
    "/docs": ["./src/content/docs/**/*.md"],
    "/docs/[slug]": ["./src/content/docs/**/*.md"],
  },
  async rewrites() {
    // server-side fallback path into the compose network
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.API_INTERNAL_URL ?? "http://api:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
