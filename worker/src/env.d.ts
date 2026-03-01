declare namespace Cloudflare {
  interface Env {
    OAUTH_REDIRECT_URL: string;
    GOOGLE_CLIENT_ID: string;
    GOOGLE_CLIENT_SECRET: string;
    GITHUB_CLIENT_ID: string;
    GITHUB_CLIENT_SECRET: string;
    LOCUSGRAPH_JWT_PRIVATE_KEY: string;
    LOCUSGRAPH_SERVER_URL?: string;
    LOCUSGRAPH_AGENT_SECRET?: string;
    LOCUSGRAPH_GRAPH_ID?: string;
    OPENAI_API_KEY?: string;
    OPENAI_MODEL?: string;
    SARVAM_API_KEY?: string;
    CORS_ORIGIN?: string;
  }
}
