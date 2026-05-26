"use client";

import React, { useState } from "react";
import { useTranslations } from "next-intl";

export default function AgentsPage() {
  const t = useTranslations("Agents");
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [prompt, setPrompt] = useState(
    "Anda adalah Luna, asisten otonom premium dari Hiqonis. Tugas Anda adalah membantu pelanggan menemukan solusi terbaik dengan natural language Bahasa Indonesia formal dan kasual..."
  );
  const [model, setModel] = useState("gemini-1.5-pro");
  const [hallucinationGuard, setHallucinationGuard] = useState(true);
  const [injectionGuard, setInjectionGuard] = useState(true);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg("");
    setTimeout(() => {
      setSaving(false);
      setSuccessMsg(t("saveSuccess"));
    }, 1200);
  };

  return (
    <div className="flex flex-col gap-8 max-w-4xl text-slate-800">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{t("title")}</h1>
        <p className="text-slate-500 text-sm font-light mt-1">
          {t("subtitle")}
        </p>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl border border-emerald-250 bg-emerald-50 text-emerald-700 text-xs font-semibold text-center animate-pulse">
          {successMsg}
        </div>
      )}

      {/* Main Settings Card */}
      <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-6">
        <h3 className="font-bold text-lg text-slate-900 border-b border-slate-200 pb-3 flex items-center gap-2">
          <span>🤖</span> {t("listTitle")}
        </h3>

        <form onSubmit={handleSave} className="flex flex-col gap-6">
          {/* System Prompt Input */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold text-slate-500 uppercase">
              {t("agentPrompt")}
            </label>
            <textarea
              rows={6}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full p-3 rounded-xl border border-slate-200 bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/10 focus:outline-none text-xs text-slate-800 leading-relaxed transition-all"
            />
          </div>

          {/* Model selection dropdown */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold text-slate-500 uppercase">
              {t("modelLabel")}
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="p-3 rounded-xl border border-slate-200 bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/10 focus:outline-none text-xs text-slate-800 transition-all cursor-pointer w-full"
            >
              <option value="gemini-1.5-pro">Google Gemini 1.5 Pro (Highly Recommended)</option>
              <option value="gpt-4o">OpenAI GPT-4o (Premium)</option>
              <option value="claude-3-5-sonnet">Anthropic Claude 3.5 Sonnet</option>
              <option value="llama-3-70b">Meta Llama 3 70b (Open Source Local)</option>
            </select>
          </div>

          {/* Guardrails Switches */}
          <div className="flex flex-col gap-4">
            <label className="text-xs font-semibold text-slate-500 uppercase">
              {t("guardrailsLabel")}
            </label>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Anti-Hallucination */}
              <div className="p-4 rounded-xl border border-slate-200/60 bg-slate-50/50 flex justify-between items-center gap-4">
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-semibold text-slate-800">{t("antiHallucination")}</span>
                  <span className="text-[9px] text-slate-500">Cross-checks response metrics with knowledge base</span>
                </div>
                <input
                  type="checkbox"
                  checked={hallucinationGuard}
                  onChange={(e) => setHallucinationGuard(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 bg-white border-slate-350 focus:ring-indigo-500/30 cursor-pointer"
                />
              </div>

              {/* Injection Shield */}
              <div className="p-4 rounded-xl border border-slate-200/60 bg-slate-50/50 flex justify-between items-center gap-4">
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-semibold text-slate-800">{t("injectionShield")}</span>
                  <span className="text-[9px] text-slate-500">Filters malicious prompt injections (OWASP guidelines)</span>
                </div>
                <input
                  type="checkbox"
                  checked={injectionGuard}
                  onChange={(e) => setInjectionGuard(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 bg-white border-slate-350 focus:ring-indigo-500/30 cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end mt-4">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:scale-[1.01] active:scale-[0.99] font-bold text-xs text-white shadow-md shadow-indigo-500/10 hover:shadow-indigo-500/25 transition-all disabled:opacity-50"
            >
              {saving ? t("saving") : t("saveButton")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
