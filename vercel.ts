import { routes, type VercelConfig } from "@vercel/config/v1";

export const config: VercelConfig = {
  rewrites: [routes.rewrite("/resume", "/resume.html")],
  headers: [
    routes.header("/resume.html", [{ key: "X-Frame-Options", value: "SAMEORIGIN" }]),
  ],
};
