"use client";

import React from "react";
import { useTranslations } from "next-intl";

export default function CRMPage() {
  const t = useTranslations("CRM");

  return (
    <div className="flex flex-col gap-8 max-w-7xl mx-auto text-slate-800">
      {/* Header */}
      <div className="flex justify-between items-start sm:items-center flex-col sm:flex-row gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{t("title")}</h1>
          <p className="text-slate-500 text-sm font-light mt-1">
            {t("subtitle")}
          </p>
        </div>
      </div>

      {/* Overview Stat Widgets */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm">
          <span className="text-xs font-semibold text-slate-500">{t("metricsTitle")}</span>
          <h2 className="text-2xl font-bold text-slate-900 mt-1">348 Leads</h2>
        </div>
        <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm">
          <span className="text-xs font-semibold text-slate-500">{t("hotLeads")}</span>
          <h2 className="text-2xl font-bold text-indigo-600 mt-1">94 Leads</h2>
        </div>
        <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm">
          <span className="text-xs font-semibold text-slate-500">{t("dealsClosed")}</span>
          <h2 className="text-2xl font-bold text-emerald-600 mt-1">Rp 45.000.000</h2>
        </div>
      </div>

      {/* Kanban Board Container */}
      <div className="flex flex-col gap-6">
        <div className="flex justify-between items-center border-b border-slate-200 pb-3">
          <h3 className="font-bold text-lg text-slate-900 flex items-center gap-2">
            <span>📋</span> {t("pipelineTitle")}
          </h3>
        </div>

        {/* Column Kanban Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 overflow-x-auto pb-4">
          
          {/* Column 1: New Leads */}
          <div className="flex flex-col gap-4 min-w-[220px]">
            <div className="flex justify-between items-center px-3 py-2 rounded-lg bg-slate-100 border border-slate-200 shrink-0">
              <span className="text-xs font-bold text-slate-700">{t("stageNew")}</span>
              <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded text-slate-600 font-bold">2</span>
            </div>
            
            <div className="flex flex-col gap-3">
              {/* Card 1 */}
              <div className="p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-500/30 hover:bg-slate-50/50 transition-all cursor-pointer shadow-sm">
                <div className="flex justify-between items-start gap-2 mb-2">
                  <span className="text-xs font-bold text-slate-800 truncate">Alice Smith</span>
                  <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" title="Hot Lead" />
                </div>
                <div className="text-[10px] text-slate-500 font-light truncate">Enterprise AI Setup</div>
                <div className="flex justify-between items-center mt-4">
                  <span className="text-[10px] font-bold text-indigo-600">Rp 15.000.000</span>
                  <span className="text-[8px] text-slate-500">Score 90</span>
                </div>
              </div>
            </div>
          </div>

          {/* Column 2: Contacted */}
          <div className="flex flex-col gap-4 min-w-[220px]">
            <div className="flex justify-between items-center px-3 py-2 rounded-lg bg-slate-100 border border-slate-200 shrink-0">
              <span className="text-xs font-bold text-slate-700">{t("stageContacted")}</span>
              <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded text-slate-600 font-bold">1</span>
            </div>

            <div className="flex flex-col gap-3">
              {/* Card 2 */}
              <div className="p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-500/30 hover:bg-slate-50/50 transition-all cursor-pointer shadow-sm">
                <div className="flex justify-between items-start gap-2 mb-2">
                  <span className="text-xs font-bold text-slate-800 truncate">Budi Santoso</span>
                  <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" title="Hot Lead" />
                </div>
                <div className="text-[10px] text-slate-500 font-light truncate">Custom Omni-Channel Bot</div>
                <div className="flex justify-between items-center mt-4">
                  <span className="text-[10px] font-bold text-indigo-600">Rp 25.000.000</span>
                  <span className="text-[8px] text-slate-500">Score 88</span>
                </div>
              </div>
            </div>
          </div>

          {/* Column 3: Qualified */}
          <div className="flex flex-col gap-4 min-w-[220px]">
            <div className="flex justify-between items-center px-3 py-2 rounded-lg bg-slate-100 border border-slate-200 shrink-0">
              <span className="text-xs font-bold text-slate-700">{t("stageQualified")}</span>
              <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded text-slate-600 font-bold">0</span>
            </div>
            
            <div className="border border-dashed border-slate-200 rounded-xl p-8 flex items-center justify-center text-slate-400 text-[10px] bg-slate-50/50">
              Empty
            </div>
          </div>

          {/* Column 4: Closed Won */}
          <div className="flex flex-col gap-4 min-w-[220px]">
            <div className="flex justify-between items-center px-3 py-2 rounded-lg bg-slate-100 border border-slate-200 shrink-0">
              <span className="text-xs font-bold text-slate-700">{t("stageClosed")}</span>
              <span className="text-[10px] bg-emerald-50 px-1.5 py-0.5 rounded text-emerald-700 font-bold border border-emerald-100">1</span>
            </div>

            <div className="flex flex-col gap-3">
              {/* Card 3 */}
              <div className="p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-500/30 hover:bg-slate-50/50 transition-all cursor-pointer shadow-sm">
                <div className="flex justify-between items-start gap-2 mb-2">
                  <span className="text-xs font-bold text-slate-500 truncate line-through decoration-slate-300">Sarah Wijaya</span>
                  <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                </div>
                <div className="text-[10px] text-slate-500 font-light truncate">Retail Support Agent</div>
                <div className="flex justify-between items-center mt-4">
                  <span className="text-[10px] font-bold text-emerald-600">Rp 12.000.000</span>
                  <span className="text-[8px] text-slate-500">Won 🎉</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
