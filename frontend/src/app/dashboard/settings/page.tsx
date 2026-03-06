"use client";

import { Settings, User, Shield, Bell, Palette, Key } from "lucide-react";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-sm text-surface-500 mt-1">
          Manage your account and preferences
        </p>
      </div>

      {/* Profile */}
      <div className="glass rounded-2xl p-6 space-y-4">
        <div className="flex items-center gap-3 mb-2">
          <User className="w-5 h-5 text-brand-400" />
          <h3 className="text-base font-semibold text-white">Profile</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-surface-500 mb-1">
              Full Name
            </label>
            <input
              type="text"
              defaultValue="Alex Johnson"
              className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white focus:outline-none focus:ring-1 focus:ring-brand-500/50"
            />
          </div>
          <div>
            <label className="block text-xs text-surface-500 mb-1">Email</label>
            <input
              type="email"
              defaultValue="alex@example.com"
              className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white focus:outline-none focus:ring-1 focus:ring-brand-500/50"
            />
          </div>
        </div>
      </div>

      {/* API Keys */}
      <div className="glass rounded-2xl p-6 space-y-4">
        <div className="flex items-center gap-3 mb-2">
          <Key className="w-5 h-5 text-brand-400" />
          <h3 className="text-base font-semibold text-white">API Keys</h3>
        </div>
        <p className="text-sm text-surface-400">
          Configure your own API keys for enhanced rate limits and custom model
          access.
        </p>
        <div className="space-y-3">
          {[
            { name: "OpenAI API Key", placeholder: "sk-..." },
            { name: "Anthropic API Key", placeholder: "sk-ant-..." },
            { name: "Twitter Bearer Token", placeholder: "AAAA..." },
          ].map((key) => (
            <div key={key.name}>
              <label className="block text-xs text-surface-500 mb-1">
                {key.name}
              </label>
              <input
                type="password"
                placeholder={key.placeholder}
                className="w-full px-4 py-2.5 rounded-xl glass text-sm text-white placeholder:text-surface-600 focus:outline-none focus:ring-1 focus:ring-brand-500/50"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Notifications */}
      <div className="glass rounded-2xl p-6 space-y-4">
        <div className="flex items-center gap-3 mb-2">
          <Bell className="w-5 h-5 text-brand-400" />
          <h3 className="text-base font-semibold text-white">Notifications</h3>
        </div>
        {[
          { label: "High-score trend alerts", description: "Get notified when a trend scores 90+" },
          { label: "Campaign completion", description: "Alert when campaign generation finishes" },
          { label: "Weekly digest", description: "Summary of trends and campaign performance" },
        ].map((item, i) => (
          <div key={i} className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm text-white">{item.label}</p>
              <p className="text-xs text-surface-500">{item.description}</p>
            </div>
            <button className="w-10 h-6 rounded-full bg-brand-600/30 relative">
              <div className="absolute right-1 top-1 w-4 h-4 rounded-full bg-brand-400 transition-all" />
            </button>
          </div>
        ))}
      </div>

      {/* Save */}
      <div className="flex justify-end">
        <button className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-500 to-accent-500 text-white text-sm font-semibold hover:shadow-lg hover:shadow-brand-500/30 transition-all">
          Save Changes
        </button>
      </div>
    </div>
  );
}
