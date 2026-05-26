"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";

export default function IndexPage() {
  const t = useTranslations("Index");

  return (
    <div className="relative min-h-screen flex flex-col justify-between overflow-hidden">
      {/* Background gradients */}
      <div className="absolute inset-0 -z-10 bg-slate-50">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/2 -right-40 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        {/* Subtle grid pattern overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-40" />
      </div>

      {/* Header */}
      <header className="w-full max-w-7xl mx-auto px-6 py-6 flex justify-between items-center border-b border-slate-200/60">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-md shadow-indigo-500/10">
            <span className="font-bold text-xl tracking-wider text-white">H</span>
          </div>
          <span className="font-bold text-2xl bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-600 bg-clip-text text-transparent tracking-tight">
            Hiqonis
          </span>
        </div>

        {/* Actions & Locale Selector */}
        <div className="flex items-center gap-4">
          {/* Locale Selector */}
          <div className="flex items-center gap-1 bg-white border border-slate-200 p-1 rounded-xl shadow-sm">
            <Link
              href="/"
              locale="id"
              className="px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all duration-200 hover:bg-slate-50 hover:text-slate-900 text-slate-600"
            >
              Bahasa
            </Link>
            <Link
              href="/"
              locale="en"
              className="px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all duration-200 hover:bg-slate-50 hover:text-slate-900 text-slate-600"
            >
              English
            </Link>
          </div>

          <Link
            href="/login"
            className="px-4 py-2 text-xs font-bold text-white rounded-xl bg-indigo-600 hover:bg-indigo-700 shadow-sm shadow-indigo-500/10 transition-all duration-300"
          >
            Sign In
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col justify-center items-center max-w-7xl mx-auto px-6 py-12 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/20 bg-indigo-500/5 text-indigo-600 text-xs font-semibold mb-6 tracking-wide backdrop-blur-md shadow-sm">
          <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
          Open-Source Bounded Context Platform
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 max-w-4xl leading-tight">
          <span className="bg-gradient-to-r from-slate-900 via-indigo-950 to-indigo-600 bg-clip-text text-transparent">
            {t("title")}
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-600 mb-10 max-w-2xl font-light leading-relaxed">
          {t("description")}
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-20">
          <Link
            href="/login"
            className="px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 font-bold text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300"
          >
            {t("dashboard")}
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-4 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 font-semibold text-slate-800 shadow-sm transition-all duration-300"
          >
            View on GitHub
          </a>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
          <div className="p-6 rounded-2xl border border-slate-200/60 bg-white/75 backdrop-blur-md hover:border-indigo-500/30 hover:bg-white shadow-sm hover:shadow-md transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-500 mb-4 font-bold text-xl shadow-inner">
              📥
            </div>
            <h3 className="font-semibold text-xl text-slate-900 mb-2">Omni-Channel Inbox</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Unified real-time interface supporting WhatsApp, Instagram, Web Chat, and email seamlessly.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-slate-200/60 bg-white/75 backdrop-blur-md hover:border-purple-500/30 hover:bg-white shadow-sm hover:shadow-md transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-purple-50 border border-purple-100 flex items-center justify-center text-purple-500 mb-4 font-bold text-xl shadow-inner">
              📚
            </div>
            <h3 className="font-semibold text-xl text-slate-900 mb-2">Knowledge Base (RAG)</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Instant retrieval chains from custom PDFs or URLs using localized pgvector embedding queries.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-slate-200/60 bg-white/75 backdrop-blur-md hover:border-blue-500/30 hover:bg-white shadow-sm hover:shadow-md transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-500 mb-4 font-bold text-xl shadow-inner">
              🤝
            </div>
            <h3 className="font-semibold text-xl text-slate-900 mb-2">Human Handoff</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Seamless operational switch between automated AI routing and human-agent intervention logic.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center border-t border-slate-200/60 text-xs text-slate-500 gap-4">
        <div>&copy; 2026 Hiqonis Platform. All rights reserved. Distributed under AGPL-3.0.</div>
        <div className="flex gap-6">
          <a href="#" className="hover:text-slate-800 transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-slate-800 transition-colors">Terms of Service</a>
          <a href="#" className="hover:text-slate-800 transition-colors">Docs</a>
        </div>
      </footer>
    </div>
  );
}
