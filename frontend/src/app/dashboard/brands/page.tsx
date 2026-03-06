"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  Briefcase,
  Edit3,
  Trash2,
  X,
  Check,
  ChevronRight,
  Target,
  Users,
  MessageSquare,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Mock brand data
// ---------------------------------------------------------------------------
const MOCK_BRANDS = [
  {
    id: "1",
    name: "EcoTech Solutions",
    industry: "technology",
    positioning: "Sustainable tech for a greener planet",
    tone: "professional",
    target_audience: {
      age_range: "25-45",
      interests: ["sustainability", "technology", "green energy"],
      demographics: "Urban professionals, environmentally conscious",
    },
    products: [
      { name: "SolarSync Pro", description: "AI-powered solar panel optimizer" },
      { name: "EcoTrack", description: "Carbon footprint tracking platform" },
    ],
    guidelines: {
      dos: ["Emphasize sustainability", "Use data-driven claims", "Professional tone"],
      donts: ["Greenwashing language", "Aggressive sales tactics"],
      voice_attributes: ["Trustworthy", "Innovative", "Grounded"],
    },
    created_at: "2024-01-15",
  },
  {
    id: "2",
    name: "VibeWear",
    industry: "fashion",
    positioning: "Streetwear that speaks. Culture-forward fashion for Gen Z.",
    tone: "casual",
    target_audience: {
      age_range: "18-28",
      interests: ["streetwear", "music", "skateboarding", "art"],
      demographics: "Gen Z, urban, creative class",
    },
    products: [
      { name: "Vibe Drop Collection", description: "Limited edition monthly drops" },
      { name: "Custom Kicks", description: "AI-designed custom sneakers" },
    ],
    guidelines: {
      dos: ["Use slang authentically", "Reference pop culture", "Be bold"],
      donts: ["Corporate speak", "Outdated references"],
      voice_attributes: ["Bold", "Authentic", "Irreverent"],
    },
    created_at: "2024-02-20",
  },
];

const INDUSTRIES = [
  "technology",
  "fashion",
  "food_beverage",
  "health_wellness",
  "finance",
  "education",
  "entertainment",
  "travel",
  "real_estate",
  "automotive",
];

const TONES = [
  "professional",
  "casual",
  "playful",
  "authoritative",
  "inspirational",
  "edgy",
];

// ---------------------------------------------------------------------------
// Component: Brand card
// ---------------------------------------------------------------------------
function BrandCard({
  brand,
  onEdit,
  onDelete,
}: {
  brand: (typeof MOCK_BRANDS)[0];
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="glass rounded-2xl p-6 hover:bg-white/10 transition-all group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-600/30 to-accent-600/30 flex items-center justify-center">
            <Briefcase className="w-6 h-6 text-brand-400" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">{brand.name}</h3>
            <span className="text-xs text-surface-500 capitalize">
              {brand.industry.replace("_", " ")} · {brand.tone}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={onEdit}
            className="p-2 rounded-lg hover:bg-white/10 text-surface-400 hover:text-white transition-colors"
          >
            <Edit3 className="w-4 h-4" />
          </button>
          <button
            onClick={onDelete}
            className="p-2 rounded-lg hover:bg-red-500/10 text-surface-400 hover:text-red-400 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <p className="text-sm text-surface-400 leading-relaxed mb-4">
        {brand.positioning}
      </p>

      <div className="space-y-3">
        {/* Audience */}
        <div className="flex items-start gap-2">
          <Users className="w-4 h-4 text-surface-500 mt-0.5 shrink-0" />
          <div className="text-xs text-surface-500">
            <span className="text-surface-300">
              {brand.target_audience.age_range}
            </span>{" "}
            · {brand.target_audience.demographics}
          </div>
        </div>

        {/* Products */}
        <div className="flex items-start gap-2">
          <Target className="w-4 h-4 text-surface-500 mt-0.5 shrink-0" />
          <div className="flex flex-wrap gap-1.5">
            {brand.products.map((p) => (
              <span
                key={p.name}
                className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-surface-400 border border-white/5"
              >
                {p.name}
              </span>
            ))}
          </div>
        </div>

        {/* Voice */}
        <div className="flex items-start gap-2">
          <MessageSquare className="w-4 h-4 text-surface-500 mt-0.5 shrink-0" />
          <div className="flex flex-wrap gap-1.5">
            {brand.guidelines.voice_attributes.map((attr) => (
              <span
                key={attr}
                className="text-xs px-2 py-0.5 rounded-full bg-brand-600/10 text-brand-400 border border-brand-500/20"
              >
                {attr}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-5 pt-4 border-t border-white/5 flex items-center justify-between">
        <span className="text-xs text-surface-600">
          Created {new Date(brand.created_at).toLocaleDateString()}
        </span>
        <button className="inline-flex items-center gap-1 text-xs text-brand-400 font-semibold hover:text-brand-300 transition-colors">
          <Sparkles className="w-3.5 h-3.5" />
          Find Matching Trends
          <ChevronRight className="w-3 h-3" />
        </button>
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Component: Create/Edit Brand Modal
// ---------------------------------------------------------------------------
function BrandModal({
  isOpen,
  onClose,
  brand,
}: {
  isOpen: boolean;
  onClose: () => void;
  brand?: (typeof MOCK_BRANDS)[0] | null;
}) {
  const [formData, setFormData] = useState({
    name: brand?.name || "",
    industry: brand?.industry || "technology",
    positioning: brand?.positioning || "",
    tone: brand?.tone || "professional",
    audience_age: brand?.target_audience?.age_range || "",
    audience_interests: brand?.target_audience?.interests?.join(", ") || "",
    audience_demographics: brand?.target_audience?.demographics || "",
    products: brand?.products?.map((p) => `${p.name}: ${p.description}`).join("\n") || "",
    voice_attributes: brand?.guidelines?.voice_attributes?.join(", ") || "",
    dos: brand?.guidelines?.dos?.join("\n") || "",
    donts: brand?.guidelines?.donts?.join("\n") || "",
  });

  if (!isOpen) return null;

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
          className="w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-surface-950 border border-white/10 rounded-2xl p-8"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">
              {brand ? "Edit Brand Profile" : "Create Brand Profile"}
            </h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-white/10 text-surface-400"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <form className="space-y-6">
            {/* Name & Industry */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-1.5">
                  Brand Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50"
                  placeholder="Your brand name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-1.5">
                  Industry
                </label>
                <select
                  value={formData.industry}
                  onChange={(e) =>
                    setFormData({ ...formData, industry: e.target.value })
                  }
                  className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white bg-transparent focus:outline-none focus:ring-1 focus:ring-brand-500/50"
                >
                  {INDUSTRIES.map((ind) => (
                    <option key={ind} value={ind} className="bg-surface-900">
                      {ind.replace("_", " ")}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Positioning */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1.5">
                Brand Positioning
              </label>
              <textarea
                value={formData.positioning}
                onChange={(e) =>
                  setFormData({ ...formData, positioning: e.target.value })
                }
                rows={2}
                className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50 resize-none"
                placeholder="Describe your brand's unique positioning in one or two sentences"
              />
            </div>

            {/* Tone */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1.5">
                Brand Tone
              </label>
              <div className="flex flex-wrap gap-2">
                {TONES.map((tone) => (
                  <button
                    key={tone}
                    type="button"
                    onClick={() => setFormData({ ...formData, tone })}
                    className={cn(
                      "px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all",
                      formData.tone === tone
                        ? "bg-brand-600/20 text-brand-400 border border-brand-500/30"
                        : "glass text-surface-400 hover:text-white"
                    )}
                  >
                    {tone}
                  </button>
                ))}
              </div>
            </div>

            {/* Target Audience */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-surface-300">
                Target Audience
              </label>
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text"
                  value={formData.audience_age}
                  onChange={(e) =>
                    setFormData({ ...formData, audience_age: e.target.value })
                  }
                  className="px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50"
                  placeholder="Age range (e.g., 25-45)"
                />
                <input
                  type="text"
                  value={formData.audience_interests}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      audience_interests: e.target.value,
                    })
                  }
                  className="px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50"
                  placeholder="Interests (comma-separated)"
                />
              </div>
              <input
                type="text"
                value={formData.audience_demographics}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    audience_demographics: e.target.value,
                  })
                }
                className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50"
                placeholder="Demographics description"
              />
            </div>

            {/* Products */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1.5">
                Products / Services (one per line — "Name: Description")
              </label>
              <textarea
                value={formData.products}
                onChange={(e) =>
                  setFormData({ ...formData, products: e.target.value })
                }
                rows={3}
                className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50 resize-none font-mono"
                placeholder="SolarSync Pro: AI-powered solar panel optimizer"
              />
            </div>

            {/* Voice Attributes */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1.5">
                Voice Attributes (comma-separated)
              </label>
              <input
                type="text"
                value={formData.voice_attributes}
                onChange={(e) =>
                  setFormData({ ...formData, voice_attributes: e.target.value })
                }
                className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50"
                placeholder="Trustworthy, Innovative, Grounded"
              />
            </div>

            {/* Guidelines */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-green-400 mb-1.5">
                  Do's (one per line)
                </label>
                <textarea
                  value={formData.dos}
                  onChange={(e) =>
                    setFormData({ ...formData, dos: e.target.value })
                  }
                  rows={3}
                  className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-green-500/50 resize-none"
                  placeholder="Emphasize sustainability"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-red-400 mb-1.5">
                  Don'ts (one per line)
                </label>
                <textarea
                  value={formData.donts}
                  onChange={(e) =>
                    setFormData({ ...formData, donts: e.target.value })
                  }
                  rows={3}
                  className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-red-500/50 resize-none"
                  placeholder="Greenwashing language"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/5">
              <button
                type="button"
                onClick={onClose}
                className="px-5 py-2.5 rounded-xl text-sm text-surface-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-500 to-accent-500 text-white text-sm font-semibold hover:shadow-lg hover:shadow-brand-500/30 transition-all"
              >
                <Check className="w-4 h-4" />
                {brand ? "Update Brand" : "Create Brand"}
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function BrandsPage() {
  const [showModal, setShowModal] = useState(false);
  const [editingBrand, setEditingBrand] = useState<
    (typeof MOCK_BRANDS)[0] | null
  >(null);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Brand Profiles</h1>
          <p className="text-sm text-surface-500 mt-1">
            Define your brand DNA for AI-powered trend matching
          </p>
        </div>
        <button
          onClick={() => {
            setEditingBrand(null);
            setShowModal(true);
          }}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 text-white text-sm font-semibold hover:bg-brand-500 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Brand
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        <AnimatePresence>
          {MOCK_BRANDS.map((brand) => (
            <BrandCard
              key={brand.id}
              brand={brand}
              onEdit={() => {
                setEditingBrand(brand);
                setShowModal(true);
              }}
              onDelete={() => {
                // Would call API in production
                console.log("Delete brand:", brand.id);
              }}
            />
          ))}
        </AnimatePresence>
      </div>

      {MOCK_BRANDS.length === 0 && (
        <div className="text-center py-20">
          <Briefcase className="w-12 h-12 text-surface-700 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-surface-400">
            No brands yet
          </h3>
          <p className="text-sm text-surface-600 mt-1 mb-6">
            Create your first brand profile to start matching trends
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 text-white text-sm font-semibold"
          >
            <Plus className="w-4 h-4" />
            Create Brand
          </button>
        </div>
      )}

      <BrandModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setEditingBrand(null);
        }}
        brand={editingBrand}
      />
    </div>
  );
}
