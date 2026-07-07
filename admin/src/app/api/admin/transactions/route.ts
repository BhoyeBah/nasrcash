import { NextResponse } from "next/server";
import { unstable_rethrow } from "next/navigation";

import { backendFetch, BackendError } from "@/lib/backend";
import type { AdminTransactionItem } from "@/lib/types";

// Thin server-side proxy so the client-side polling widget (TanStack Query)
// can refetch without ever holding the admin JWT in browser JS.
export async function GET() {
  try {
    const transactions = await backendFetch<AdminTransactionItem[]>(
      "/api/v1/admin/transactions?limit=10",
    );
    return NextResponse.json(transactions);
  } catch (error) {
    unstable_rethrow(error); // let redirect()/notFound() control-flow errors propagate
    if (error instanceof BackendError) {
      return NextResponse.json({ message: error.message }, { status: error.status });
    }
    return NextResponse.json({ message: "Backend unreachable" }, { status: 502 });
  }
}
