"use client";

import React from "react";
import { useTranslations } from "next-intl";

export default function KnowledgeBasePage() {
  const t = useTranslations("Knowledge");

  return (
    <div className="flex flex-col gap-8 max-w-5xl text-slate-800">
      {/* Page Header */}
      <div className="flex justify-between items-start gap-4 flex-col sm:flex-row">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{t("title")}</h1>
          <p className="text-slate-500 text-sm font-light mt-1">
            {t("subtitle")}
          </p>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Input Forms */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          {/* File Upload card */}
          <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-4">
            <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wide">{t("uploadTitle")}</h3>
            <p className="text-xs text-slate-500 font-light">Supports PDF, DOCX, TXT (Max 10MB)</p>
            
            <div className="border border-dashed border-slate-200 hover:border-indigo-500 rounded-xl p-8 flex flex-col items-center justify-center gap-3 bg-slate-50/50 hover:bg-slate-50 cursor-pointer transition-all">
              <span className="text-3xl">📤</span>
              <span className="text-xs font-semibold text-slate-700 text-center">{t("dropzone")}</span>
            </div>
          </div>

          {/* Sync Website URL Card */}
          <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-4">
            <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wide">{t("urlLabel")}</h3>
            
            <div className="flex flex-col gap-2">
              <input
                type="url"
                placeholder="https://example.com/faq"
                className="p-3 rounded-xl border border-slate-200 bg-white focus:border-indigo-500 focus:outline-none text-xs text-slate-800 transition-all w-full"
              />
              <button className="w-full py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-800 shadow-sm transition-all">
                {t("ingestButton")}
              </button>
            </div>
          </div>
        </div>

        {/* Right Status List */}
        <div className="lg:col-span-2 p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-6">
          <h3 className="font-bold text-lg text-slate-900">{t("docListTitle")}</h3>

          <div className="flex flex-col gap-4">
            {/* Active Doc */}
            <div className="p-4 rounded-xl border border-slate-200/60 bg-white flex justify-between items-center hover:border-indigo-500/30 transition-all shadow-sm">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📄</span>
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-slate-900">Panduan_Layanan_Hiqonis.pdf</span>
                  <span className="text-[10px] text-slate-500">1.2 MB • 48 Chunks</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[10px] font-bold border border-emerald-100">{t("statusActive")}</span>
                <span className="text-xs text-slate-400 cursor-pointer hover:text-red-500 transition-colors">🗑️</span>
              </div>
            </div>

            {/* In-processing Doc */}
            <div className="p-4 rounded-xl border border-slate-200/60 bg-white flex justify-between items-center hover:border-indigo-500/30 transition-all shadow-sm">
              <div className="flex items-center gap-3">
                <span className="text-2xl animate-pulse">🌐</span>
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-slate-900">https://hiqonis.com/faq-layanan</span>
                  <span className="text-[10px] text-slate-500">Crawling & Embedding generator</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 text-[10px] font-bold border border-indigo-100 animate-pulse">{t("statusProcessing")}</span>
                <span className="text-xs text-slate-400 cursor-pointer hover:text-red-500 transition-colors">🗑️</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
