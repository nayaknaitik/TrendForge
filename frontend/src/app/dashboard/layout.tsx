"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Zap,
  TrendingUp,
  Briefcase,
  Rocket,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Trends", icon: TrendingUp },
  { href: "/dashboard/brands", label: "Brands", icon: Briefcase },
  { href: "/dashboard/campaigns", label: "Campaigns", icon: Rocket },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface-950 flex">
      {/* -------- Sidebar (desktop) -------- */}
      <aside className="hidden lg:flex flex-col w-64 border-r border-white/5 bg-surface-950/80 backdrop-blur-xl fixed inset-y-0 left-0 z-40">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-white/5">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">
              Trend<span className="text-brand-400">Forge</span>
            </span>
          </Link>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all",
                  isActive
                    ? "bg-brand-600/15 text-brand-400"
                    : "text-surface-400 hover:text-white hover:bg-white/5"
                )}
              >
                <item.icon className="w-4.5 h-4.5" />
                {item.label}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-brand-400"
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* User / Logout */}
        <div className="px-3 py-4 border-t border-white/5">
          <button className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm text-surface-500 hover:text-white hover:bg-white/5 transition-all w-full">
            <LogOut className="w-4 h-4" />
            Log out
          </button>
        </div>
      </aside>

      {/* -------- Mobile sidebar -------- */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: "spring", damping: 25 }}
              className="fixed inset-y-0 left-0 w-64 bg-surface-950 border-r border-white/5 z-50 lg:hidden flex flex-col"
            >
              <div className="px-6 py-5 flex items-center justify-between border-b border-white/5">
                <Link href="/" className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
                    <Zap className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-lg font-bold text-white">
                    Trend<span className="text-brand-400">Forge</span>
                  </span>
                </Link>
                <button onClick={() => setSidebarOpen(false)}>
                  <X className="w-5 h-5 text-surface-400" />
                </button>
              </div>
              <nav className="flex-1 px-3 py-4 space-y-1">
                {NAV_ITEMS.map((item) => {
                  const isActive =
                    pathname === item.href ||
                    (item.href !== "/dashboard" &&
                      pathname.startsWith(item.href));
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setSidebarOpen(false)}
                      className={cn(
                        "flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all",
                        isActive
                          ? "bg-brand-600/15 text-brand-400"
                          : "text-surface-400 hover:text-white hover:bg-white/5"
                      )}
                    >
                      <item.icon className="w-4.5 h-4.5" />
                      {item.label}
                    </Link>
                  );
                })}
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* -------- Main content area -------- */}
      <div className="flex-1 lg:ml-64">
        {/* Top bar (mobile) */}
        <header className="lg:hidden sticky top-0 z-30 border-b border-white/5 bg-surface-950/80 backdrop-blur-xl px-4 py-3 flex items-center justify-between">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu className="w-5 h-5 text-surface-300" />
          </button>
          <span className="text-sm font-semibold text-white">TrendForge</span>
          <div className="w-5" />
        </header>

        <main className="p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
