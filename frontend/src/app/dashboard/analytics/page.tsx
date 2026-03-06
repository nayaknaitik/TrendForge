"use client";

import { motion } from "framer-motion";
import {
  BarChart3,
  TrendingUp,
  Target,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5 },
  }),
};

// Mock analytics
const STATS = [
  {
    label: "Campaigns Generated",
    value: "47",
    change: "+12%",
    positive: true,
    icon: Zap,
  },
  {
    label: "Trends Analyzed",
    value: "2,841",
    change: "+28%",
    positive: true,
    icon: TrendingUp,
  },
  {
    label: "Avg. Engagement Rate",
    value: "5.8%",
    change: "+0.7%",
    positive: true,
    icon: Target,
  },
  {
    label: "Avg. Predicted CTR",
    value: "3.4%",
    change: "-0.2%",
    positive: false,
    icon: BarChart3,
  },
];

const TOP_CAMPAIGNS = [
  { name: "AI Art x EcoTech", ctr: "5.2%", engagement: "8.4%", platform: "twitter" },
  { name: "VibeWear Sustainable Drop", ctr: "4.8%", engagement: "9.1%", platform: "tiktok" },
  { name: "Deep Work Productivity", ctr: "3.9%", engagement: "6.2%", platform: "linkedin" },
  { name: "Minimalist Packaging", ctr: "3.5%", engagement: "7.3%", platform: "instagram" },
];

const WEEKLY = [
  { day: "Mon", campaigns: 8, trends: 423 },
  { day: "Tue", campaigns: 12, trends: 510 },
  { day: "Wed", campaigns: 6, trends: 380 },
  { day: "Thu", campaigns: 15, trends: 620 },
  { day: "Fri", campaigns: 9, trends: 445 },
  { day: "Sat", campaigns: 3, trends: 210 },
  { day: "Sun", campaigns: 4, trends: 253 },
];

export default function AnalyticsPage() {
  const maxTrends = Math.max(...WEEKLY.map((w) => w.trends));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-sm text-surface-500 mt-1">
          Campaign performance overview — last 30 days
        </p>
      </div>

      {/* Stat cards */}
      <motion.div
        initial="hidden"
        animate="visible"
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {STATS.map((stat, i) => (
          <motion.div
            key={i}
            variants={fadeUp}
            custom={i}
            className="glass rounded-xl p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-surface-500">{stat.label}</span>
              <stat.icon className="w-4 h-4 text-brand-400" />
            </div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
            <div className="flex items-center gap-1 mt-1">
              {stat.positive ? (
                <ArrowUpRight className="w-3.5 h-3.5 text-green-400" />
              ) : (
                <ArrowDownRight className="w-3.5 h-3.5 text-red-400" />
              )}
              <span
                className={cn(
                  "text-xs font-medium",
                  stat.positive ? "text-green-400" : "text-red-400"
                )}
              >
                {stat.change}
              </span>
              <span className="text-xs text-surface-600">vs last month</span>
            </div>
          </motion.div>
        ))}
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Weekly bar chart */}
        <div className="lg:col-span-2 glass rounded-2xl p-6">
          <h3 className="text-sm font-semibold text-surface-300 mb-6">
            Weekly Activity
          </h3>
          <div className="flex items-end gap-3 h-48">
            {WEEKLY.map((w, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full flex flex-col items-center gap-1">
                  <div
                    className="w-full max-w-[32px] rounded-t-lg bg-gradient-to-t from-brand-600 to-brand-400 transition-all"
                    style={{
                      height: `${(w.trends / maxTrends) * 160}px`,
                    }}
                  />
                </div>
                <span className="text-xs text-surface-500">{w.day}</span>
                <span className="text-[10px] text-surface-600">
                  {w.trends} trends
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Top campaigns */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-sm font-semibold text-surface-300 mb-4">
            Top Performing Campaigns
          </h3>
          <div className="space-y-3">
            {TOP_CAMPAIGNS.map((c, i) => (
              <div
                key={i}
                className="flex items-center justify-between py-2 border-b border-white/5 last:border-0"
              >
                <div>
                  <p className="text-sm text-white font-medium">{c.name}</p>
                  <span className="text-xs text-surface-500 capitalize">
                    {c.platform}
                  </span>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-green-400">
                    {c.engagement}
                  </p>
                  <span className="text-xs text-surface-500">CTR: {c.ctr}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
