"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Rocket,
  Clock,
  ChevronRight,
  Download,
  Trash2,
  Eye,
  X,
  Twitter,
  Instagram,
  Globe,
  Linkedin,
  Play,
  Copy,
  Check,
  Sparkles,
  Target,
  BarChart3,
  TrendingUp,
  Zap,
  MessageSquare,
  Hash,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Mock campaign data
// ---------------------------------------------------------------------------
const MOCK_CAMPAIGNS = [
  {
    id: "1",
    campaign_name: "AI Art x EcoTech — Sustainable Innovation Angle",
    campaign_angle:
      "Position EcoTech as the intersection of cutting-edge AI and sustainability, riding the AI Art wave.",
    brand_name: "EcoTech Solutions",
    trend_title: "#AIArt revolution hits mainstream media",
    status: "ready",
    strategy: {
      hook_strategy: "Lead with the stunning visual of AI meeting sustainability",
      target_platforms: ["twitter", "linkedin", "instagram"],
      content_pillars: [
        "AI Innovation",
        "Sustainable Future",
        "Visual Impact",
      ],
      key_messages: [
        "Technology and sustainability aren't opposites — they're partners",
        "AI-powered solutions for a greener tomorrow",
      ],
      suggested_budget_range: "$500-$2,000",
      suggested_duration_days: 7,
    },
    estimated_engagement: {
      overall_reach: 125000,
      estimated_ctr: 3.2,
      estimated_engagement_rate: 5.8,
    },
    ad_copies: [
      {
        id: "a1",
        platform: "twitter",
        ad_format: "thread",
        hook: "What if AI art could literally save the planet? 🌍",
        body: "The #AIArt revolution isn't just about pretty pictures.\n\nAt EcoTech, we've been using the same generative AI principles to optimize solar panels — and the results are staggering.\n\nOur SolarSync Pro has improved energy capture by 34% using AI pattern recognition.\n\nThe same creativity powering viral AI art is powering the green energy revolution.",
        cta: "Try SolarSync Pro free for 30 days → link.eco/solar",
        hashtags: ["#AIArt", "#Sustainability", "#CleanTech", "#SolarEnergy"],
        predicted_engagement_rate: 5.2,
        slides: null,
      },
      {
        id: "a2",
        platform: "linkedin",
        ad_format: "text",
        hook: "Everyone's talking about AI art. We're talking about AI impact.",
        body: "While the world marvels at AI-generated masterpieces, our team at EcoTech Solutions has been applying the same generative AI principles to solve a very different challenge: clean energy optimization.\n\nOur SolarSync Pro platform uses neural networks to optimize solar panel configurations, resulting in 34% better energy capture for our clients.\n\nThe AI art revolution proves something we've believed since day one: AI's greatest canvas isn't pixels — it's the planet.",
        cta: "See how AI is powering sustainable energy →",
        hashtags: [
          "#CleanTech",
          "#AIInnovation",
          "#Sustainability",
          "#FutureOfEnergy",
        ],
        predicted_engagement_rate: 4.1,
        slides: null,
      },
      {
        id: "a3",
        platform: "instagram",
        ad_format: "carousel",
        hook: "AI art is beautiful. But what if AI could make the PLANET beautiful? 🌱",
        body: "Swipe to see how the same AI behind viral art is powering the green energy revolution →",
        cta: "Link in bio: Start your sustainability journey with EcoTech",
        hashtags: [
          "#AIArt",
          "#Sustainability",
          "#CleanEnergy",
          "#EcoTech",
          "#GreenTech",
        ],
        predicted_engagement_rate: 6.8,
        slides: [
          "Slide 1: Bold text — 'AI Art is trending. But what about AI Impact?'",
          "Slide 2: Split screen — AI art vs. AI-optimized solar farm",
          "Slide 3: Stats — '34% better energy capture with AI'",
          "Slide 4: Product shot — SolarSync Pro dashboard",
          "Slide 5: CTA — 'Join the AI-powered sustainability revolution'",
        ],
      },
    ],
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "2",
    campaign_name: "VibeWear x Sustainable Fashion — Street Meets Green",
    campaign_angle:
      "Position VibeWear as the brand that proves street style and sustainability can coexist.",
    brand_name: "VibeWear",
    trend_title: "Sustainable fashion hauls breaking records",
    status: "ready",
    strategy: {
      hook_strategy: "Challenge the assumption that sustainable = boring",
      target_platforms: ["tiktok", "instagram", "twitter"],
      content_pillars: ["Street Culture", "Sustainability", "Self-Expression"],
      key_messages: [
        "Drip doesn't have to cost the earth",
        "The future of streetwear is sustainable and fire",
      ],
      suggested_budget_range: "$1,000-$3,000",
      suggested_duration_days: 14,
    },
    estimated_engagement: {
      overall_reach: 250000,
      estimated_ctr: 4.5,
      estimated_engagement_rate: 8.2,
    },
    ad_copies: [
      {
        id: "b1",
        platform: "tiktok",
        ad_format: "reel_script",
        hook: "POV: Your entire fit is sustainable and still fire 🔥",
        body: "[0-3s] Quick cuts: model pulling VibeWear pieces from a thrift-style rack\n[3-7s] Full outfit reveal — slow-mo spin\n[7-12s] Text overlay: 'Every piece: recycled materials'\n[12-15s] Close-up on quality details\n[15-18s] Text: '87% less water. 100% more drip.'\n[18-20s] Logo + CTA",
        cta: "Link in bio — new drop this Friday 🛒",
        hashtags: [
          "#SustainableFashion",
          "#OOTD",
          "#VibeWear",
          "#EcoFashion",
          "#StreetStyle",
        ],
        predicted_engagement_rate: 9.1,
        slides: null,
      },
    ],
    created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
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

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  ready: { bg: "bg-green-500/10", text: "text-green-400" },
  draft: { bg: "bg-yellow-500/10", text: "text-yellow-400" },
  generating: { bg: "bg-brand-500/10", text: "text-brand-400" },
  archived: { bg: "bg-surface-500/10", text: "text-surface-400" },
};

// ---------------------------------------------------------------------------
// Component: Ad copy preview with copy-to-clipboard
// ---------------------------------------------------------------------------
function AdCopyPreview({ ad }: { ad: (typeof MOCK_CAMPAIGNS)[0]["ad_copies"][0] }) {
  const [copied, setCopied] = useState<string | null>(null);
  const PlatformIcon = PLATFORM_ICONS[ad.platform] || Globe;

  const copyText = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopied(field);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="glass rounded-xl p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-gradient-to-r text-white",
              PLATFORM_COLORS[ad.platform]
            )}
          >
            <PlatformIcon className="w-3 h-3" />
            {ad.platform}
          </span>
          <span className="text-xs text-surface-500 capitalize bg-white/5 px-2 py-0.5 rounded">
            {ad.ad_format.replace("_", " ")}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <TrendingUp className="w-3.5 h-3.5 text-green-400" />
          <span className="text-xs font-semibold text-green-400">
            {ad.predicted_engagement_rate}% predicted
          </span>
        </div>
      </div>

      {/* Hook */}
      <div className="relative group/hook">
        <label className="text-xs text-surface-500 font-medium mb-1 block">
          Hook
        </label>
        <p className="text-sm font-semibold text-white leading-relaxed">
          {ad.hook}
        </p>
        <button
          onClick={() => copyText(ad.hook, "hook")}
          className="absolute top-0 right-0 p-1 rounded opacity-0 group-hover/hook:opacity-100 transition-opacity text-surface-500 hover:text-white"
        >
          {copied === "hook" ? (
            <Check className="w-3.5 h-3.5 text-green-400" />
          ) : (
            <Copy className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Body */}
      <div className="relative group/body">
        <label className="text-xs text-surface-500 font-medium mb-1 block">
          Body
        </label>
        <p className="text-sm text-surface-300 leading-relaxed whitespace-pre-line">
          {ad.body}
        </p>
        <button
          onClick={() => copyText(ad.body, "body")}
          className="absolute top-0 right-0 p-1 rounded opacity-0 group-hover/body:opacity-100 transition-opacity text-surface-500 hover:text-white"
        >
          {copied === "body" ? (
            <Check className="w-3.5 h-3.5 text-green-400" />
          ) : (
            <Copy className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* CTA */}
      <div className="relative group/cta">
        <label className="text-xs text-surface-500 font-medium mb-1 block">
          Call to Action
        </label>
        <p className="text-sm text-brand-400 font-semibold">{ad.cta}</p>
        <button
          onClick={() => copyText(ad.cta, "cta")}
          className="absolute top-0 right-0 p-1 rounded opacity-0 group-hover/cta:opacity-100 transition-opacity text-surface-500 hover:text-white"
        >
          {copied === "cta" ? (
            <Check className="w-3.5 h-3.5 text-green-400" />
          ) : (
            <Copy className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Carousel slides (if applicable) */}
      {ad.slides && ad.slides.length > 0 && (
        <div>
          <label className="text-xs text-surface-500 font-medium mb-2 block">
            Carousel Slides
          </label>
          <div className="space-y-2">
            {ad.slides.map((slide, i) => (
              <div
                key={i}
                className="text-xs text-surface-400 bg-white/5 rounded-lg px-3 py-2"
              >
                {slide}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hashtags */}
      <div>
        <label className="text-xs text-surface-500 font-medium mb-1.5 block">
          Hashtags
        </label>
        <div className="flex flex-wrap gap-1.5">
          {ad.hashtags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-0.5 text-xs px-2 py-0.5 rounded-full bg-brand-600/10 text-brand-400 border border-brand-500/20 cursor-pointer hover:bg-brand-600/20 transition-colors"
              onClick={() => copyText(tag, tag)}
            >
              <Hash className="w-2.5 h-2.5" />
              {tag.replace("#", "")}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component: Campaign detail modal
// ---------------------------------------------------------------------------
function CampaignDetailModal({
  campaign,
  onClose,
}: {
  campaign: (typeof MOCK_CAMPAIGNS)[0] | null;
  onClose: () => void;
}) {
  if (!campaign) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-surface-950 border border-white/10 rounded-2xl"
        >
          {/* Header */}
          <div className="sticky top-0 bg-surface-950/95 backdrop-blur-xl border-b border-white/5 px-8 py-5 flex items-start justify-between z-10">
            <div>
              <h2 className="text-xl font-bold text-white">
                {campaign.campaign_name}
              </h2>
              <div className="flex items-center gap-3 mt-1.5">
                <span className="text-xs text-surface-500">
                  {campaign.brand_name}
                </span>
                <span className="text-xs text-surface-600">·</span>
                <span className="text-xs text-surface-500">
                  {campaign.trend_title}
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-white/10 text-surface-400"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-8 space-y-8">
            {/* Strategy overview */}
            <div>
              <h3 className="text-sm font-semibold text-surface-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Target className="w-4 h-4 text-brand-400" />
                Campaign Strategy
              </h3>
              <div className="glass rounded-xl p-6 space-y-4">
                <p className="text-sm text-surface-300 leading-relaxed">
                  {campaign.campaign_angle}
                </p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <span className="text-xs text-surface-500">Platforms</span>
                    <div className="flex gap-1.5 mt-1">
                      {campaign.strategy.target_platforms.map((p) => {
                        const Icon = PLATFORM_ICONS[p] || Globe;
                        return (
                          <span
                            key={p}
                            className={cn(
                              "inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-gradient-to-r text-white",
                              PLATFORM_COLORS[p]
                            )}
                          >
                            <Icon className="w-2.5 h-2.5" />
                            {p}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs text-surface-500">Duration</span>
                    <p className="text-sm text-white mt-1">
                      {campaign.strategy.suggested_duration_days} days
                    </p>
                  </div>
                  <div>
                    <span className="text-xs text-surface-500">Budget</span>
                    <p className="text-sm text-white mt-1">
                      {campaign.strategy.suggested_budget_range}
                    </p>
                  </div>
                  <div>
                    <span className="text-xs text-surface-500">
                      Hook Strategy
                    </span>
                    <p className="text-xs text-surface-300 mt-1">
                      {campaign.strategy.hook_strategy}
                    </p>
                  </div>
                </div>

                {/* Key messages */}
                <div>
                  <span className="text-xs text-surface-500">Key Messages</span>
                  <ul className="mt-1.5 space-y-1">
                    {campaign.strategy.key_messages.map((msg, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm text-surface-300"
                      >
                        <MessageSquare className="w-3.5 h-3.5 text-brand-400 mt-0.5 shrink-0" />
                        {msg}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Performance estimates */}
            <div>
              <h3 className="text-sm font-semibold text-surface-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-brand-400" />
                Estimated Performance
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {[
                  {
                    label: "Estimated Reach",
                    value: `${(campaign.estimated_engagement.overall_reach / 1000).toFixed(0)}K`,
                    icon: TrendingUp,
                    color: "text-brand-400",
                  },
                  {
                    label: "Predicted CTR",
                    value: `${campaign.estimated_engagement.estimated_ctr}%`,
                    icon: Target,
                    color: "text-green-400",
                  },
                  {
                    label: "Engagement Rate",
                    value: `${campaign.estimated_engagement.estimated_engagement_rate}%`,
                    icon: Zap,
                    color: "text-amber-400",
                  },
                ].map((stat, i) => (
                  <div key={i} className="glass rounded-xl p-4 text-center">
                    <stat.icon
                      className={cn("w-5 h-5 mx-auto mb-2", stat.color)}
                    />
                    <div className="text-xl font-bold text-white">
                      {stat.value}
                    </div>
                    <div className="text-xs text-surface-500 mt-1">
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Ad Copies */}
            <div>
              <h3 className="text-sm font-semibold text-surface-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-brand-400" />
                Generated Ad Copies ({campaign.ad_copies.length})
              </h3>
              <div className="space-y-4">
                {campaign.ad_copies.map((ad) => (
                  <AdCopyPreview key={ad.id} ad={ad} />
                ))}
              </div>
            </div>

            {/* Export buttons */}
            <div className="flex items-center gap-3 pt-4 border-t border-white/5">
              <button className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 text-white text-sm font-semibold hover:bg-brand-500 transition-colors">
                <Download className="w-4 h-4" />
                Export JSON
              </button>
              <button className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl glass text-surface-300 text-sm font-medium hover:text-white hover:bg-white/10 transition-all">
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function CampaignsPage() {
  const [selectedCampaign, setSelectedCampaign] = useState<
    (typeof MOCK_CAMPAIGNS)[0] | null
  >(null);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Campaigns</h1>
          <p className="text-sm text-surface-500 mt-1">
            AI-generated campaigns with platform-specific ad copies
          </p>
        </div>
      </div>

      {/* Campaign cards */}
      <div className="space-y-4">
        {MOCK_CAMPAIGNS.map((campaign, i) => {
          const statusStyle = STATUS_STYLES[campaign.status] || STATUS_STYLES.draft;
          return (
            <motion.div
              key={campaign.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass rounded-2xl p-6 hover:bg-white/10 transition-all group cursor-pointer"
              onClick={() => setSelectedCampaign(campaign)}
            >
              <div className="flex flex-col lg:flex-row lg:items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <span
                      className={cn(
                        "text-xs font-semibold px-2.5 py-1 rounded-full capitalize",
                        statusStyle.bg,
                        statusStyle.text
                      )}
                    >
                      {campaign.status}
                    </span>
                    <span className="text-xs text-surface-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(campaign.created_at).toLocaleString()}
                    </span>
                  </div>

                  <h3 className="text-base font-semibold text-white group-hover:text-brand-300 transition-colors mb-1">
                    {campaign.campaign_name}
                  </h3>
                  <p className="text-sm text-surface-400 line-clamp-1 mb-3">
                    {campaign.campaign_angle}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-surface-500">
                    <span>Brand: {campaign.brand_name}</span>
                    <span>·</span>
                    <span>
                      {campaign.ad_copies.length} ad cop
                      {campaign.ad_copies.length !== 1 ? "ies" : "y"}
                    </span>
                    <span>·</span>
                    <div className="flex gap-1">
                      {campaign.strategy.target_platforms.map((p) => {
                        const Icon = PLATFORM_ICONS[p] || Globe;
                        return <Icon key={p} className="w-3.5 h-3.5 text-surface-500" />;
                      })}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <div className="text-center">
                    <div className="text-xs text-surface-500 mb-1">CTR</div>
                    <div className="text-lg font-bold text-green-400">
                      {campaign.estimated_engagement.estimated_ctr}%
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-surface-500 mb-1">Reach</div>
                    <div className="text-lg font-bold text-brand-400">
                      {(campaign.estimated_engagement.overall_reach / 1000).toFixed(0)}
                      K
                    </div>
                  </div>
                  <button className="p-2 rounded-lg hover:bg-white/10 text-surface-400 hover:text-white transition-colors">
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {MOCK_CAMPAIGNS.length === 0 && (
        <div className="text-center py-20">
          <Rocket className="w-12 h-12 text-surface-700 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-surface-400">
            No campaigns yet
          </h3>
          <p className="text-sm text-surface-600 mt-1">
            Go to the Trends page and generate a campaign from a trending topic
          </p>
        </div>
      )}

      <CampaignDetailModal
        campaign={selectedCampaign}
        onClose={() => setSelectedCampaign(null)}
      />
    </div>
  );
}
