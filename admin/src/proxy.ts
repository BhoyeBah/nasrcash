import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { ADMIN_TOKEN_COOKIE } from "@/lib/session";

// UX-level gate only — every Server Component/Action re-checks the token
// against the backend on each request, so this is not the security boundary.
export function proxy(request: NextRequest) {
  const hasToken = request.cookies.has(ADMIN_TOKEN_COOKIE);
  const { pathname } = request.nextUrl;

  if (!hasToken && pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (!hasToken && pathname === "/") {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (hasToken && (pathname === "/login" || pathname === "/")) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/login", "/dashboard/:path*"],
};
