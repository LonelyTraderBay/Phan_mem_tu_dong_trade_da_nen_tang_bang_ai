import type { Metadata } from "next";
import { KillSwitchBar } from "@/components/KillSwitchBar";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bot Auto Trade",
  description: "Multi-platform AI trading bot frontend",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-50 text-neutral-900 antialiased">
        <KillSwitchBar />
        <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
