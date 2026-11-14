import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/AppShell";
import { SummaryProvider } from "@/lib/summary-context";
import { AppStateProvider } from "@/lib/url-state";

export const metadata: Metadata = {
  title: "EARTH//NEXT",
  description:
    "Case-file investigation tool for Earth-system trends. NASA Space Apps 2026.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-bg text-text font-sans antialiased">
        <SummaryProvider>
          <AppStateProvider>
            <AppShell>{children}</AppShell>
          </AppStateProvider>
        </SummaryProvider>
      </body>
    </html>
  );
}
