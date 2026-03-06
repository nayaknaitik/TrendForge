"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  TrendingUp,
  RefreshCw,
  Filter,
  Search,
  ArrowUpRight,
  Twitter,
  Instagram,
  Globe,
  Linkedin,
  Play,
  Clock,
  Zap,
  ChevronDown,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Mock trend data (would come from API in production)
// ---------------------------------------------------------------------------
const MOCK_TRENDS = [
  {
    id: "1",
    platform: "twitter",
    title: "#AIArt revolution hits mainstream media",
    description:
      "Major outlets covering the explosion of AI-generated art on social media. 4.2M posts in the last 24 hours with accelerating engagement.",
    topics: ["AI", "Art", "Technology"],
    keywords: ["midjourney", "stable diffusion", "ai art"],
    sentiment_label: "positive",
    sentiment_score: 0.82,
    trend_score: 94,
    engagement_velocity: 15230,
    volume: 4200000,
    content_format: "thread",
    detected_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "2",
    platform: "reddit",
    title: "Deep Work productivity methods going viral on r/Productivity",
    description:
      "Cal Newport's deep work methodology seeing a resurgence with new time-blocking apps. 890K upvotes across related posts.",
    topics: ["Productivity", "Self-improvement", "Work"],
    keywords: ["deep work", "time blocking", "focus"],
    sentiment_label: "positive",
    sentiment_score: 0.75,
    trend_score: 87,
    engagement_velocity: 8920,
    volume: 890000,
    content_format: "text",
    detected_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "3",
    platform: "instagram",
    title: "Minimalist packaging design trend — 2.1M reels",
    description:
      "Brands pivoting to ultra-minimalist packaging. Unboxing content with clean, simple designs getting 3x normal engagement.",
    topics: ["Design", "Packaging", "E-commerce"],
    keywords: ["minimalist", "packaging", "design"],
    sentiment_label: "neutral",
    sentiment_score: 0.55,
    trend_score: 91,
    engagement_velocity: 12100,
    volume: 2100000,
    content_format: "carousel",
    detected_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "4",
    platform: "tiktok",
    title: "Sustainable fashion hauls breaking records",
    description:
      "Gen Z creators leading a wave of thrift/vintage fashion hauls. Sustainability messaging resonating strongly.",
    topics: ["Fashion", "Sustainability", "Gen Z"],
    keywords: ["sustainable fashion", "thrift", "vintage"],
    sentiment_label: "positive",
    sentiment_score: 0.88,
    trend_score: 82,
    engagement_velocity: 6450,
    volume: 890000,
    content_format: "video",
    detected_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "5",
    platform: "linkedin",
    title: "Remote-first culture debate resurfaces with major layoffs",
    description:
      "CEOs and employees clashing on remote work mandates. Highly polarized engagement with strong opinion pieces.",
    topics: ["Remote Work", "Corporate Culture", "Leadership"],
    keywords: ["remote work", "RTO", "hybrid"],
    sentiment_label: "mixed",
    sentiment_score: 0.35,
    trend_score: 78,
    engagement_velocity: 4200,
    volume: 420000,
    content_format: "text",
    detected_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "6",
    platform: "twitter",
    title: "No-code tool adoption skyrockets among startups",
    description:
      "Bubble, Webflow, and Framer adoption trending hard as bootstrapped founders share build-in-public journeys.",
    topics: ["No-code", "Startups", "Technology"],
    keywords: ["no-code", "bubble", "webflow"],
    sentiment_label: "positive",
    sentiment_score: 0.79,
    trend_score: 85,
    engagement_velocity: 7800,
    volume: 560000,
    content_format: "thread",
    detected_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
  },
];

const PLATFORM_ICONS: Record<string, React.ElementType> = {
  twitter: Twitter,
  reddit: Globe,
  instagram: Instagram,
  tiktok: Play,
  linkedin: Linkedin,
};

const PLATFORM_COLORS: Record<string, string> = {
  twitter: "from-blue-500 to-cyan-400",
  reddit: "from-orange-500 to-red-400",
  instagram: "from-pink-500 to-purple-400",
  tiktok: "from-green-500 to-emerald-400",
  linkedin: "from-indigo-500 to-blue-400",
};

const SENTIMENT_COLORS: Record<string, string> = {
  positive: "bg-green-400",
  neutral: "bg-yellow-400",
  negative: "bg-red-400",
  mixed: "bg-orange-400",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function timeAgo(date: string) {
  const diff = Date.now() - new Date(date).getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return "< 1h ago";
  return `${hours}h ago`;
}

function formatNumber(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function TrendsDashboard() {
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);

  const filteredTrends = MOCK_TRENDS.filter((t) => {
    if (selectedPlatform && t.platform !== selectedPlatform) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        t.title.toLowerCase().includes(q) ||
        t.topics.some((topic) => topic.toLowerCase().includes(q)) ||
        t.keywords.some((kw) => kw.toLowerCase().includes(q))
      );
    }
    return true;
  });

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsRefreshing(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Trend Feed</h1>
          <p className="text-sm text-surface-500 mt-1">
            Real-time trends across 5 platforms · Updated every 5 minutes
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 text-white text-sm font-semibold hover:bg-brand-500 transition-colors disabled:opacity-60"
        >
          <RefreshCw
            className={cn("w-4 h-4", isRefreshing && "animate-spin")}
          />
          {isRefreshing ? "Scanning..." : "Refresh Trends"}
        </button>
      </div>

      {/* Filters bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
          <input
            type="text"
            placeholder="Search trends, topics, keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50"
          />
        </div>

        {/* Platform filter */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setSelectedPlatform(null)}
            className={cn(
              "px-3 py-2 rounded-lg text-xs font-medium transition-all",
              !selectedPlatform
                ? "bg-brand-600/20 text-brand-400 border border-brand-500/30"
                : "glass text-surface-400 hover:text-white"
            )}
          >
            All
          </button>
          {Object.keys(PLATFORM_ICONS).map((platform) => {
            const Icon = PLATFORM_ICONS[platform];
            return (
              <button
                key={platform}
                onClick={() =>
                  setSelectedPlatform(
                    selectedPlatform === platform ? null : platform
                  )
                }
                className={cn(
                  "inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all capitalize",
                  selectedPlatform === platform
                    ? "bg-brand-600/20 text-brand-400 border border-brand-500/30"
                    : "glass text-surface-400 hover:text-white"
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                {platform}
              </button>
            );
          })}
        </div>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          {
            label: "Active Trends",
            value: filteredTrends.length.toString(),
            icon: TrendingUp,
            color: "text-brand-400",
          },
          {
            label: "Avg Score",
            value: (
              filteredTrends.reduce((a, t) => a + t.trend_score, 0) /
              filteredTrends.length
            ).toFixed(0),
            icon: Zap,
            color: "text-amber-400",
          },
          {
            label: "Total Engagement",
            value: formatNumber(
              filteredTrends.reduce((a, t) => a + t.volume, 0)
            ),
            icon: ArrowUpRight,
            color: "text-green-400",
          },
          {
            label: "Last Scan",
            value: "2 min ago",
            icon: Clock,
            color: "text-surface-400",
          },
        ].map((stat, i) => (
          <div key={i} className="glass rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-surface-500">{stat.label}</span>
              <stat.icon className={cn("w-4 h-4", stat.color)} />
            </div>
            <div className="text-xl font-bold text-white">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Trend cards */}
      <div className="space-y-4">
        {filteredTrends.map((trend, i) => {
          const PlatformIcon = PLATFORM_ICONS[trend.platform] || Globe;
          return (
            <motion.div
              key={trend.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass rounded-2xl p-6 hover:bg-white/10 transition-all group cursor-pointer"
            >
              <div className="flex flex-col lg:flex-row lg:items-start gap-4">
                {/* Left — Main info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <span
                      className={cn(
                        "inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-gradient-to-r text-white",
                        PLATFORM_COLORS[trend.platform]
                      )}
                    >
                      <PlatformIcon className="w-3 h-3" />
                      {trend.platform}
                    </span>
                    <span className="text-xs text-surface-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {timeAgo(trend.detected_at)}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span
                        className={cn(
                          "w-2 h-2 rounded-full",
                          SENTIMENT_COLORS[trend.sentiment_label]
                        )}
                      />
                      <span className="text-xs text-surface-500 capitalize">
                        {trend.sentiment_label}
                      </span>
                    </div>
                  </div>

                  <h3 className="text-base font-semibold text-white group-hover:text-brand-300 transition-colors mb-2">
                    {trend.title}
                  </h3>
                  <p className="text-sm text-surface-400 leading-relaxed line-clamp-2">
                    {trend.description}
                  </p>

                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {trend.topics.map((topic) => (
                      <span
                        key={topic}
                        className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-surface-400 border border-white/5"
                      >
                        {topic}
                      </span>
                    ))}
                    <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-surface-500 capitalize border border-white/5">
                      {trend.content_format}
                    </span>
                  </div>
                </div>

                {/* Right — Score + metrics */}
                <div className="flex lg:flex-col items-center lg:items-end gap-4 lg:gap-3 shrink-0">
                  {/* Score */}
                  <div className="text-center lg:text-right">
                    <div className="text-xs text-surface-500 mb-1">
                      Trend Score
                    </div>
                    <div
                      className={cn(
                        "text-2xl font-bold font-mono",
                        trend.trend_score >= 90
                          ? "text-green-400"
                          : trend.trend_score >= 80
                          ? "text-brand-400"
                          : trend.trend_score >= 70
                          ? "text-amber-400"
                          : "text-surface-400"
                      )}
                    >
                      {trend.trend_score}
                    </div>
                  </div>

                  <div className="flex gap-4 lg:gap-6">
                    <div className="text-center">
                      <div className="text-xs text-surface-500">Volume</div>
                      <div className="text-sm font-semibold text-white">
                        {formatNumber(trend.volume)}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-surface-500">Velocity</div>
                      <div className="text-sm font-semibold text-white">
                        {formatNumber(trend.engagement_velocity)}/h
                      </div>
                    </div>
                  </div>

                  {/* Generate campaign button */}
                  <button className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-brand-600/20 text-brand-400 text-xs font-semibold hover:bg-brand-600/30 transition-colors">
                    <Rocket className="w-3.5 h-3.5" />
                    Generate Campaign
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredTrends.length === 0 && (
        <div className="text-center py-20">
          <Filter className="w-12 h-12 text-surface-700 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-surface-400">
            No trends found
          </h3>
          <p className="text-sm text-surface-600 mt-1">
            Try adjusting your filters or refresh to fetch new trends
          </p>
        </div>
      )}
    </div>
  );
}
