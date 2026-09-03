import type { Metadata } from "next";
import { Inter, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppShell } from "@/components/shell/AppShell";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});



export const metadata: Metadata = {
  title: "FinancePilot AI",
  description: "AI-assisted financial reconciliation & audit platform",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${plexMono.variable} font-sans antialiased bg-bg-app text-text-primary`}
      >
        <Providers>
          <TooltipProvider>
            <AppShell>
              {children}
            </AppShell>
            <Toaster />
          </TooltipProvider>
        </Providers>
      </body>
    </html>
  );
}
