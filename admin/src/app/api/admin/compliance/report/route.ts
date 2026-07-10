import { NextResponse } from "next/server";

import { getAdminToken } from "@/lib/session";

const BACKEND_URL = process.env.NASRCASH_API_URL ?? "http://localhost:8000";

export async function GET() {
  const token = await getAdminToken();
  if (!token) {
    return NextResponse.json({ message: "Non authentifié" }, { status: 401 });
  }

  const response = await fetch(`${BACKEND_URL}/api/v1/admin/compliance/report`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    return NextResponse.json(
      { message: body?.message ?? "Export impossible" },
      { status: response.status },
    );
  }

  const csv = await response.text();
  return new NextResponse(csv, {
    headers: {
      "Content-Type": "text/csv",
      "Content-Disposition": "attachment; filename=compliance_report.csv",
    },
  });
}
