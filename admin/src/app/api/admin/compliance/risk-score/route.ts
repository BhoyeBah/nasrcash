import { NextRequest, NextResponse } from "next/server";
import { unstable_rethrow } from "next/navigation";

import { backendFetch, BackendError } from "@/lib/backend";
import type { RiskScore } from "@/lib/types";

export async function GET(request: NextRequest) {
  const userId = request.nextUrl.searchParams.get("userId");
  if (!userId) {
    return NextResponse.json({ message: "userId requis" }, { status: 400 });
  }

  try {
    const score = await backendFetch<RiskScore>(
      `/api/v1/admin/compliance/users/${userId}/risk-score`,
    );
    return NextResponse.json(score);
  } catch (error) {
    unstable_rethrow(error);
    if (error instanceof BackendError) {
      return NextResponse.json({ message: error.message }, { status: error.status });
    }
    return NextResponse.json({ message: "Backend unreachable" }, { status: 502 });
  }
}
