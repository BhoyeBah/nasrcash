import { redirect } from "next/navigation";

import { getAdminToken } from "@/lib/session";

export default async function RootPage() {
  const token = await getAdminToken();
  redirect(token ? "/dashboard" : "/login");
}
