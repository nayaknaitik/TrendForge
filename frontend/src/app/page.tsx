"use client";

import { motion } from "framer-motion";
import {
  Zap,
  BarChart3,
  Brain,
  Layers,
  ArrowRight,
  TrendingUp,
  Target,
  Sparkles,
  Shield,
  Globe,
  Clock,
  ChevronRight,
  Check,
  Twitter,
  Instagram,
  Linkedin,
  Play,
} from "lucide-react";
import Link from "next/link";

// ---------------------------------------------------------------------------
// Animation helpers
// ---------------------------------------------------------------------------
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] },
  }),
};

const stagger = {
  visible: { transition: { staggerChildren: 0.08 } },
};

// ---------------------------------------------------------------------------
// Mock data for the animated trend feed
// ---------------------------------------------------------------------------
const MOCK_TRENDS = [
  {
    platform: "Twitter",
    title: "#AIArt explosion — 4.2M posts in 24h",
    score: 94,
    sentiment: "positive",
    color: "from-blue-500 to-cyan-400",
  },
  {
    platform: "Reddit",
    title: "r/Productivity goes viral with 'Deep Work' hacks",
    score: 87,
    sentiment: "positive",
    color: "from-orange-500 to-red-400",
  },
  {
    platform: "Instagram",
    title: "Minimalist packaging design trend — 2.1M reels",
    score: 91,
    sentiment: "neutral",
    color: "from-pink-500 to-purple-400",
  },
  {
    platform: "TikTok",
    title: "Sustainable fashion hauls — 890K creates",
    score: 82,
    sentiment: "positive",
    color: "from-green-500 to-emerald-400",
  },
  {
    platform: "LinkedIn",
    title: "Remote-first culture debate resurfaces — 420K engagements",
    score: 78,
    sentiment: "mixed",
    color: "from-indigo-500 to-blue-400",
  },
];

const PLATFORMS = [
  { name: "Twitter / X", icon: Twitter },
  { name: "Instagram", icon: Instagram },
  { name: "LinkedIn", icon: Linkedin },
  { name: "Reddit", icon: Globe },
  { name: "TikTok", icon: Play },
];

// ---------------------------------------------------------------------------
// Component: Animated trend card in the hero section
// ---------------------------------------------------------------------------
function TrendCard({
  trend,
  index,
}: {
  trend: (typeof MOCK_TRENDS)[0];
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 60, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ delay: 0.8 + index * 0.15, duration: 0.5 }}
      className="glass rounded-xl p-4 mb-3 hover:bg-white/10 transition-colors cursor-default group"
    >
      <div className="flex items-center justify-between mb-2">
        <span
          className={`text-xs font-semibold px-2 py-0.5 rounded-full bg-gradient-to-r ${trend.color} text-white`}
        >
          {trend.platform}
        </span>
        <span className="text-sm font-mono text-brand-400 font-bold">
          {trend.score}
        </span>
      </div>
      <p className="text-sm text-surface-200 group-hover:text-white transition-colors leading-snug">
        {trend.title}
      </p>
      <div className="mt-2 flex items-center gap-2">
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            trend.sentiment === "positive"
              ? "bg-green-400"
              : trend.sentiment === "neutral"
              ? "bg-yellow-400"
              : "bg-orange-400"
          }`}
        />
        <span className="text-xs text-surface-500">{trend.sentiment}</span>
        <div className="ml-auto">
          <TrendingUp className="w-3.5 h-3.5 text-brand-400 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Component: Step card for the "How It Works" section
// ---------------------------------------------------------------------------
function StepCard({
  step,
  index,
}: {
  step: { icon: React.ElementType; title: string; description: string };
  index: number;
}) {
  return (
    <motion.div
      variants={fadeUp}
      custom={index}
      className="relative glass rounded-2xl p-8 text-center group hover:bg-white/10 transition-all duration-300"
    >
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-sm font-bold text-white shadow-lg shadow-brand-600/40">
        {index + 1}
      </div>
      <div className="w-14 h-14 mx-auto mb-5 rounded-xl bg-gradient-to-br from-brand-600/20 to-accent-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
        <step.icon className="w-7 h-7 text-brand-400" />
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
      <p className="text-sm text-surface-400 leading-relaxed">
        {step.description}
      </p>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Component: Feature card
// ---------------------------------------------------------------------------
function FeatureCard({
  feature,
  index,
}: {
  feature: {
    icon: React.ElementType;
    title: string;
    description: string;
    tag?: string;
  };
  index: number;
}) {
  return (
    <motion.div
      variants={fadeUp}
      custom={index}
      className="glass rounded-2xl p-6 group hover:bg-white/10 transition-all duration-300 hover:shadow-lg hover:shadow-brand-900/20"
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 shrink-0 rounded-xl bg-gradient-to-br from-brand-600/20 to-accent-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
          <feature.icon className="w-6 h-6 text-brand-400" />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-semibold text-white">
              {feature.title}
            </h3>
            {feature.tag && (
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-accent-600/20 text-accent-400 uppercase tracking-wider">
                {feature.tag}
              </span>
            )}
          </div>
          <p className="text-sm text-surface-400 leading-relaxed">
            {feature.description}
          </p>
        </div>
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Component: Pricing card
// ---------------------------------------------------------------------------
function PricingCard({
  plan,
  index,
}: {
  plan: {
    name: string;
    price: string;
    period: string;
    description: string;
    features: string[];
    popular?: boolean;
    cta: string;
  };
  index: number;
}) {
  return (
    <motion.div
      variants={fadeUp}
      custom={index}
      className={`relative rounded-2xl p-8 ${
        plan.popular
          ? "bg-gradient-to-b from-brand-900/60 to-surface-950 border-2 border-brand-500/50 shadow-xl shadow-brand-900/30"
          : "glass"
      }`}
    >
      {plan.popular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-brand-500 to-accent-500 text-xs font-bold text-white">
          MOST POPULAR
        </div>
      )}
      <h3 className="text-xl font-bold text-white mb-1">{plan.name}</h3>
      <p className="text-sm text-surface-400 mb-6">{plan.description}</p>
      <div className="mb-6">
        <span className="text-4xl font-bold text-white">{plan.price}</span>
        <span className="text-surface-500 ml-1">{plan.period}</span>
      </div>
      <ul className="space-y-3 mb-8">
        {plan.features.map((f, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-surface-300">
            <Check className="w-4 h-4 text-brand-400 mt-0.5 shrink-0" />
            {f}
          </li>
        ))}
      </ul>
      <button
        className={`w-full py-3 rounded-xl font-semibold text-sm transition-all ${
          plan.popular
            ? "bg-gradient-to-r from-brand-500 to-accent-500 text-white hover:shadow-lg hover:shadow-brand-500/30 hover:scale-[1.02]"
            : "bg-surface-800 text-surface-200 hover:bg-surface-700"
        }`}
      >
        {plan.cta}
      </button>
    </motion.div>
  );
}

// ===========================================================================
// PAGE
// ===========================================================================
export default function LandingPage() {
  const steps = [
    {
      icon: Globe,
      title: "Real-Time Scanning",
      description:
        "Our scrapers monitor Twitter, Reddit, Instagram, TikTok and LinkedIn 24 / 7, ingesting millions of signals every hour.",
    },
    {
      icon: Brain,
      title: "AI Classification",
      description:
        "A multi-agent system classifies trends, scores sentiment, measures velocity, and predicts virality using GPT-4 and Claude.",
    },
    {
      icon: Target,
      title: "Brand Matching",
      description:
        "Semantic, audience, and industry vectors are compared against your brand DNA to surface only the most relevant trends.",
    },
    {
      icon: Sparkles,
      title: "Campaign Generation",
      description:
        "Platform-optimised ad copy, hooks, CTAs and creative briefs are generated and scored for predicted engagement.",
    },
  ];

  const features = [
    {
      icon: TrendingUp,
      title: "Engagement Velocity Tracking",
      description:
        "Spot explosive trends before competitors with sub-minute engagement velocity calculation.",
      tag: "Real-time",
    },
    {
      icon: Layers,
      title: "Multi-Agent Pipeline",
      description:
        "Five specialised AI agents work in concert — from classification to copy generation to performance prediction.",
    },
    {
      icon: BarChart3,
      title: "Performance Heuristics",
      description:
        "Every generated ad copy comes with predicted CTR, engagement rate, and confidence intervals.",
      tag: "AI",
    },
    {
      icon: Shield,
      title: "Brand Safety Guardrails",
      description:
        "Tone, topic, and audience guardrails ensure every recommendation aligns with your brand guidelines.",
    },
    {
      icon: Clock,
      title: "Campaign in 30 Seconds",
      description:
        "From trend detection to fully-formed multi-platform campaign — complete pipeline under 30s.",
    },
    {
      icon: Zap,
      title: "Multi-Platform Export",
      description:
        "Export ad copies formatted for Twitter threads, Instagram carousels, LinkedIn posts, TikTok scripts, and more.",
    },
  ];

  const plans = [
    {
      name: "Starter",
      price: "$49",
      period: "/mo",
      description: "For individuals & small teams",
      features: [
        "3 brand profiles",
        "100 trend analyses / month",
        "5 campaigns / month",
        "Twitter + Reddit scrapers",
        "Email support",
      ],
      cta: "Start Free Trial",
    },
    {
      name: "Growth",
      price: "$149",
      period: "/mo",
      description: "For growing marketing teams",
      features: [
        "10 brand profiles",
        "Unlimited trend analyses",
        "50 campaigns / month",
        "All 5 platform scrapers",
        "Advanced analytics",
        "CSV & JSON export",
        "Priority support",
      ],
      popular: true,
      cta: "Start Free Trial",
    },
    {
      name: "Enterprise",
      price: "$499",
      period: "/mo",
      description: "For agencies & large teams",
      features: [
        "Unlimited brand profiles",
        "Unlimited everything",
        "Custom AI model fine-tuning",
        "API access",
        "White-label exports",
        "Dedicated account manager",
        "SSO & audit logs",
      ],
      cta: "Contact Sales",
    },
  ];

  return (
    <div className="min-h-screen bg-surface-950 overflow-hidden">
      {/* ----------------------------------------------------------------- */}
      {/* Background grid + glow */}
      {/* ----------------------------------------------------------------- */}
      <div className="fixed inset-0 bg-grid-pattern bg-grid-40 opacity-30 pointer-events-none" />
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-radial from-brand-600/15 via-transparent to-transparent pointer-events-none blur-3xl" />

      {/* ----------------------------------------------------------------- */}
      {/* Navbar */}
      {/* ----------------------------------------------------------------- */}
      <nav className="relative z-50 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">
              Trend<span className="text-brand-400">Forge</span>
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-surface-400 hover:text-white transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-sm text-surface-400 hover:text-white transition-colors">
              How It Works
            </a>
            <a href="#pricing" className="text-sm text-surface-400 hover:text-white transition-colors">
              Pricing
            </a>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-sm text-surface-300 hover:text-white transition-colors"
            >
              Log in
            </Link>
            <Link
              href="/signup"
              className="text-sm font-semibold px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-500 to-accent-500 text-white hover:shadow-lg hover:shadow-brand-500/30 hover:scale-[1.02] transition-all"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ----------------------------------------------------------------- */}
      {/* HERO SECTION */}
      {/* ----------------------------------------------------------------- */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-20 lg:pt-32 lg:pb-28">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left — Copy */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs text-surface-300 mb-8"
            >
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              Scanning 5 platforms in real-time
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.1 }}
              className="text-5xl lg:text-6xl xl:text-7xl font-bold leading-[1.05] tracking-tight text-balance"
            >
              Turn{" "}
              <span className="gradient-text">viral trends</span>
              <br />
              into high-converting
              <br />
              <span className="gradient-text">ad campaigns</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="mt-6 text-lg text-surface-400 max-w-xl leading-relaxed"
            >
              TrendForge's multi-agent AI detects emerging trends across social
              platforms, matches them to your brand DNA, and generates
              platform-ready campaigns — all in under 30 seconds.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45, duration: 0.5 }}
              className="mt-10 flex flex-wrap items-center gap-4"
            >
              <Link
                href="/signup"
                className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-r from-brand-500 to-accent-500 text-white font-semibold text-base hover:shadow-xl hover:shadow-brand-500/30 hover:scale-[1.02] transition-all"
              >
                Start Free Trial
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </Link>
              <Link
                href="#how-it-works"
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl glass text-surface-300 font-medium text-sm hover:text-white hover:bg-white/10 transition-all"
              >
                See How It Works
                <ChevronRight className="w-4 h-4" />
              </Link>
            </motion.div>

            {/* Platforms bar */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="mt-12 flex items-center gap-5 flex-wrap"
            >
              <span className="text-xs text-surface-600 uppercase tracking-wider">
                Sources:
              </span>
              {PLATFORMS.map((p) => (
                <div
                  key={p.name}
                  className="flex items-center gap-1.5 text-xs text-surface-500"
                >
                  <p.icon className="w-3.5 h-3.5" />
                  {p.name}
                </div>
              ))}
            </motion.div>
          </div>

          {/* Right — Animated Trend Feed */}
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-radial from-brand-600/10 via-transparent to-transparent blur-2xl" />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="relative glass rounded-2xl p-6 max-w-md mx-auto lg:ml-auto"
            >
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse" />
                  <span className="text-sm font-semibold text-white">
                    Live Trend Feed
                  </span>
                </div>
                <span className="text-xs text-surface-500 font-mono">
                  {new Date().toLocaleDateString()}
                </span>
              </div>

              {MOCK_TRENDS.map((trend, i) => (
                <TrendCard key={i} trend={trend} index={i} />
              ))}

              <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
                <span className="text-xs text-surface-500">
                  142 trends detected today
                </span>
                <span className="text-xs text-brand-400 font-semibold">
                  View All →
                </span>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* Social proof bar */}
      {/* ----------------------------------------------------------------- */}
      <section className="relative z-10 border-y border-white/5 bg-surface-950/80">
        <div className="max-w-7xl mx-auto px-6 py-10">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={stagger}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center"
          >
            {[
              { value: "5M+", label: "Trends Analyzed" },
              { value: "< 30s", label: "Campaign Generation" },
              { value: "5", label: "Social Platforms" },
              { value: "3.2x", label: "Avg. CTR Improvement" },
            ].map((stat, i) => (
              <motion.div key={i} variants={fadeUp} custom={i}>
                <div className="text-3xl font-bold gradient-text mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-surface-500">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* HOW IT WORKS */}
      {/* ----------------------------------------------------------------- */}
      <section id="how-it-works" className="relative z-10 max-w-7xl mx-auto px-6 py-24">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.span
            variants={fadeUp}
            className="text-xs font-semibold uppercase tracking-wider text-brand-400"
          >
            How It Works
          </motion.span>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="text-3xl md:text-4xl font-bold text-white mt-3 text-balance"
          >
            From raw signal to ready campaign
            <br />
            <span className="gradient-text">in four intelligent steps</span>
          </motion.h2>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          variants={stagger}
          className="grid md:grid-cols-2 xl:grid-cols-4 gap-6"
        >
          {steps.map((step, i) => (
            <StepCard key={i} step={step} index={i} />
          ))}
        </motion.div>
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* FEATURES */}
      {/* ----------------------------------------------------------------- */}
      <section id="features" className="relative z-10 max-w-7xl mx-auto px-6 py-24">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.span
            variants={fadeUp}
            className="text-xs font-semibold uppercase tracking-wider text-brand-400"
          >
            Platform Features
          </motion.span>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="text-3xl md:text-4xl font-bold text-white mt-3 text-balance"
          >
            Built for marketing teams
            <br />
            <span className="gradient-text">who move at internet speed</span>
          </motion.h2>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          variants={stagger}
          className="grid md:grid-cols-2 xl:grid-cols-3 gap-5"
        >
          {features.map((feature, i) => (
            <FeatureCard key={i} feature={feature} index={i} />
          ))}
        </motion.div>
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* DEMO PREVIEW — Pipeline Visualization */}
      {/* ----------------------------------------------------------------- */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-24">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.span
            variants={fadeUp}
            className="text-xs font-semibold uppercase tracking-wider text-brand-400"
          >
            AI Pipeline
          </motion.span>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="text-3xl md:text-4xl font-bold text-white mt-3 text-balance"
          >
            Five agents. One mission.
            <br />
            <span className="gradient-text">Maximum relevance, zero noise.</span>
          </motion.h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="glass rounded-2xl p-8 md:p-12"
        >
          <div className="flex flex-col md:flex-row items-stretch gap-4">
            {[
              {
                agent: "Classifier",
                desc: "Categorises raw social signals into topics, formats, and sentiment",
                color: "brand-500",
              },
              {
                agent: "Relevance",
                desc: "Scores each trend against your brand's semantic DNA",
                color: "purple-500",
              },
              {
                agent: "Strategist",
                desc: "Creates a campaign angle, messaging pillars, and platform mix",
                color: "cyan-500",
              },
              {
                agent: "Copywriter",
                desc: "Generates platform-optimised hooks, body copy, CTAs & hashtags",
                color: "pink-500",
              },
              {
                agent: "Predictor",
                desc: "Estimates engagement rates, CTR, and provides optimisation tips",
                color: "amber-500",
              },
            ].map((a, i) => (
              <div key={i} className="flex-1 flex flex-col items-center text-center">
                <div
                  className={`w-12 h-12 rounded-xl bg-${a.color}/20 flex items-center justify-center mb-3`}
                >
                  <Brain className={`w-6 h-6 text-${a.color}`} />
                </div>
                <h4 className="text-sm font-bold text-white mb-1">
                  {a.agent} Agent
                </h4>
                <p className="text-xs text-surface-400 leading-relaxed">
                  {a.desc}
                </p>
                {i < 4 && (
                  <ChevronRight className="hidden md:block w-5 h-5 text-surface-600 mt-4 rotate-0 md:rotate-0" />
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* PRICING */}
      {/* ----------------------------------------------------------------- */}
      <section id="pricing" className="relative z-10 max-w-7xl mx-auto px-6 py-24">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.span
            variants={fadeUp}
            className="text-xs font-semibold uppercase tracking-wider text-brand-400"
          >
            Pricing
          </motion.span>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="text-3xl md:text-4xl font-bold text-white mt-3 text-balance"
          >
            Simple pricing.{" "}
            <span className="gradient-text">Unlimited potential.</span>
          </motion.h2>
          <motion.p
            variants={fadeUp}
            custom={2}
            className="mt-4 text-surface-400 max-w-md mx-auto"
          >
            Start free. Upgrade when you're ready to scale.
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          variants={stagger}
          className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto"
        >
          {plans.map((plan, i) => (
            <PricingCard key={i} plan={plan} index={i} />
          ))}
        </motion.div>
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* CTA */}
      {/* ----------------------------------------------------------------- */}
      <section className="relative z-10 max-w-4xl mx-auto px-6 py-24 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="rounded-3xl bg-gradient-to-br from-brand-900/60 via-surface-950 to-accent-900/40 border border-white/10 p-12 md:p-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 text-balance">
            Stop reacting. Start{" "}
            <span className="gradient-text">anticipating.</span>
          </h2>
          <p className="text-surface-400 max-w-lg mx-auto mb-8">
            Join marketing teams using TrendForge to turn real-time social
            intelligence into high-converting campaigns before their
            competitors even notice the trend.
          </p>
          <Link
            href="/signup"
            className="group inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-brand-500 to-accent-500 text-white font-semibold text-base hover:shadow-xl hover:shadow-brand-500/30 hover:scale-[1.02] transition-all"
          >
            Start Your Free Trial
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <p className="mt-4 text-xs text-surface-600">
            No credit card required · 14-day free trial · Cancel anytime
          </p>
        </motion.div>
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* Footer */}
      {/* ----------------------------------------------------------------- */}
      <footer className="relative z-10 border-t border-white/5 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
                <Zap className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold text-white">
                Trend<span className="text-brand-400">Forge</span>
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm text-surface-500">
              <a href="#" className="hover:text-white transition-colors">
                Privacy
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Terms
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Docs
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Support
              </a>
            </div>
            <p className="text-xs text-surface-600">
              &copy; {new Date().getFullYear()} TrendForge. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
