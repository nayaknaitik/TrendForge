import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";

export const metadata: Metadata = {
  title: "TrendForge — AI Marketing Intelligence",
  description:
    "Real-time AI-powered trend detection and ad generation platform. Turn viral moments into high-converting campaigns in seconds.",
  keywords: [
    "AI marketing",
    "ad generation",
    "trend detection",
    "social media marketing",
    "campaign automation",
  ],
  openGraph: {
    title: "TrendForge — AI Marketing Intelligence",
    description:
      "Turn viral moments into high-converting campaigns in seconds.",
    siteName: "TrendForge",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${GeistSans.variable} ${GeistMono.variable} font-sans min-h-screen`}
      >
        {children}
      </body>
    </html>
  );
}
