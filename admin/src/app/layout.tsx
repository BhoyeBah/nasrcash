import type { Metadata } from "next";
import "./globals.css";

import { QueryProvider } from "@/components/query-provider";

export const metadata: Metadata = {
  title: "NasrCash Admin",
  description: "Back-office administrateur NasrCash",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
