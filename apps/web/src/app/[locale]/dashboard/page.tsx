"use client";

import React, { useState } from "react";
import { useTranslations } from "next-intl";

export default function DashboardPage() {
  const t = useTranslations("Dashboard");
  const [timeFilter, setTimeFilter] = useState("7d");
  const [activeHoverPoint, setActiveHoverPoint] = useState<number | null>(null);

  // Simulated metrics matching backend calculations
  const metrics = {
    totalConversations: 1248,
    aiHandled: 1153,
    humanHandoff: 95,
    aiRate: "92.4%",
    handoffRate: "7.6%",
    csat: 4.8,
    averageFrt: "42s",
    averageRt: "3m 15s"
  };

  // 7-day conversation volume history
  const chartData = [
    { day: "Mon", count: 120 },
    { day: "Tue", count: 150 },
    { day: "Wed", count: 210 },
    { day: "Thu", count: 180 },
    { day: "Fri", count: 240 },
    { day: "Sat", count: 160 },
    { day: "Sun", count: 188 }
  ];

  // SVG Area Chart Dimensions
  const chartWidth = 500;
  const chartHeight = 160;
  const maxCount = 300;

  // Calculate SVG Points for Area & Line
  const points = chartData.map((data, i) => {
    const x = (i / (chartData.length - 1)) * (chartWidth - 40) + 20;
    const y = chartHeight - (data.count / maxCount) * (chartHeight - 40) - 20;
    return { x, y, ...data };
  });

  const pathD = `M ${points.map(p => `${p.x} ${p.y}`).join(" L ")}`;
  const areaD = `${pathD} L ${points[points.length - 1].x} ${chartHeight - 20} L ${points[0].x} ${chartHeight - 20} Z`;

  // CSAT survey ratings distribution
  const csatDistribution = [
    { stars: 5, percentage: 80, count: 96 },
    { stars: 4, percentage: 12, count: 14 },
    { stars: 3, percentage: 5, count: 6 },
    { stars: 2, percentage: 2, count: 2 },
    { stars: 1, percentage: 1, count: 1 }
  ];

  // Trigger simulated report export
  const handleExportCSV = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Date Created,Channel,Status,Human Handoff Active,First Response Time (sec),Resolution Time (sec),Total Messages\n"
      + "2026-05-26 20:15:00,whatsapp,resolved,No,42,195,4\n"
      + "2026-05-26 19:40:00,instagram,resolved,No,35,140,2\n"
      + "2026-05-26 18:10:00,web,resolved,Yes,50,600,6\n";
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `hiqonis_analytics_report_${timeFilter}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col gap-8 text-slate-800">
      {/* Header and Quick Filters */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{t("title")}</h1>
          <p className="text-slate-500 text-sm font-light mt-1">{t("subtitle")}</p>
        </div>
        <div className="flex items-center gap-3 bg-white border border-slate-200 p-1.5 rounded-xl shadow-sm">
          <button 
            onClick={() => setTimeFilter("7d")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${timeFilter === "7d" ? "bg-indigo-600 text-white shadow-md" : "text-slate-600 hover:text-slate-900"}`}
          >
            {t("time7d")}
          </button>
          <button 
            onClick={() => setTimeFilter("30d")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${timeFilter === "30d" ? "bg-indigo-600 text-white shadow-md" : "text-slate-600 hover:text-slate-900"}`}
          >
            {t("time30d")}
          </button>
          <button 
            onClick={handleExportCSV}
            className="px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg text-xs font-bold text-slate-800 transition-all flex items-center gap-1.5 shadow-sm"
          >
            <span>📥</span> {t("export")}
          </button>
        </div>
      </div>

      {/* Overview Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Card 1: Total Conversations */}
        <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm hover:shadow-md transition-all duration-300">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">{t("totalConvs")}</span>
          <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-2">{metrics.totalConversations}</h3>
          <span className="text-[10px] text-indigo-600 font-semibold block mt-1">↑ 12% vs last week</span>
        </div>

        {/* Card 2: AI Handled Rate */}
        <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm hover:shadow-md transition-all duration-300">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">{t("aiRate")}</span>
          <h3 className="text-3xl font-extrabold text-emerald-600 tracking-tight mt-2">{metrics.aiRate}</h3>
          <span className="text-[10px] text-slate-500 block mt-1">{metrics.aiHandled} {t("aiHandled")}</span>
        </div>

        {/* Card 3: CSAT */}
        <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm hover:shadow-md transition-all duration-300">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">{t("csat")}</span>
          <h3 className="text-3xl font-extrabold text-amber-500 tracking-tight mt-2">{metrics.csat} / 5.0</h3>
          <span className="text-[10px] text-amber-500 font-semibold block mt-1">⭐⭐⭐⭐⭐ (Excellent)</span>
        </div>

        {/* Card 4: Response Durations */}
        <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm hover:shadow-md transition-all duration-300">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">{t("frt")}</span>
          <h3 className="text-3xl font-extrabold text-indigo-600 tracking-tight mt-2">{metrics.averageFrt}</h3>
          <span className="text-[10px] text-slate-500 block mt-1">{t("rt")}: {metrics.averageRt}</span>
        </div>
      </div>

      {/* Main Charts & Table section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Area Chart (2/3 width) */}
        <div className="lg:col-span-2 p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-4">
          <div className="flex justify-between items-center">
            <h3 className="font-bold text-lg text-slate-900">{t("volumeTitle")}</h3>
            <span className="text-slate-500 text-[10px]">Real-time analytics</span>
          </div>

          {/* SVG Line & Area Render */}
          <div className="relative w-full h-48 border border-slate-100 bg-slate-50/50 rounded-xl overflow-hidden flex items-center justify-center shadow-inner">
            <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-full">
              {/* Gridlines */}
              <line x1="20" y1="40" x2="480" y2="40" stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4" />
              <line x1="20" y1="80" x2="480" y2="80" stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4" />
              <line x1="20" y1="120" x2="480" y2="120" stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4" />

              {/* Area path */}
              <path d={areaD} fill="url(#indigoGrad)" opacity="0.1" />

              {/* Line path */}
              <path d={pathD} fill="none" stroke="#6366f1" strokeWidth="3" strokeLinecap="round" />

              {/* Dynamic Interactive Nodes */}
              {points.map((p, i) => (
                <g key={i}>
                  <circle
                    cx={p.x}
                    cy={p.y}
                    r={activeHoverPoint === i ? 6 : 4}
                    fill={activeHoverPoint === i ? "#a855f7" : "#6366f1"}
                    stroke="#ffffff"
                    strokeWidth="1.5"
                    className="cursor-pointer transition-all"
                    onMouseEnter={() => setActiveHoverPoint(i)}
                    onMouseLeave={() => setActiveHoverPoint(null)}
                  />
                  {/* Hover tooltips */}
                  {activeHoverPoint === i && (
                    <g>
                      <rect
                        x={p.x - 30}
                        y={p.y - 32}
                        width="60"
                        height="20"
                        rx="4"
                        fill="#0f172a"
                        stroke="#4f46e5"
                        strokeWidth="1"
                      />
                      <text
                        x={p.x}
                        y={p.y - 18}
                        fill="#ffffff"
                        fontSize="9"
                        fontWeight="bold"
                        textAnchor="middle"
                      >
                        {p.count} chats
                      </text>
                    </g>
                  )}
                  {/* X Axis Labels */}
                  <text
                    x={p.x}
                    y={chartHeight - 4}
                    fill="#64748b"
                    fontSize="9"
                    fontWeight="semibold"
                    textAnchor="middle"
                  >
                    {p.day}
                  </text>
                </g>
              ))}

              {/* Gradients */}
              <defs>
                <linearGradient id="indigoGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>

        {/* Right Bars Chart (1/3 width) */}
        <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-4">
          <h3 className="font-bold text-lg text-slate-900">{t("csatTitle")}</h3>

          <div className="flex flex-col gap-3.5 mt-2">
            {csatDistribution.map((dist, idx) => (
              <div key={idx} className="flex flex-col gap-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-amber-500">{"⭐".repeat(dist.stars)}</span>
                  <span className="text-slate-600">{dist.count} chats ({dist.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-100 h-2 border border-slate-200/60 rounded-full overflow-hidden shadow-inner">
                  <div 
                    className="bg-gradient-to-r from-amber-500 to-amber-300 h-full rounded-full transition-all duration-500" 
                    style={{ width: `${dist.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Lower Recent Conversations Table */}
      <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-4">
        <h3 className="font-bold text-lg text-slate-900">{t("recentConvs")}</h3>

        <div className="w-full overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-100 text-slate-500 uppercase tracking-wider font-bold">
                <th className="py-3 px-4">{t("columnCustomer")}</th>
                <th className="py-3 px-4">{t("columnChannel")}</th>
                <th className="py-3 px-4">{t("columnStatus")}</th>
                <th className="py-3 px-4">{t("columnAction")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-light text-slate-700">
              <tr className="hover:bg-slate-50 transition-colors">
                <td className="py-4 px-4 font-semibold text-slate-900">Budi Santoso</td>
                <td className="py-4 px-4"><span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100 text-[9px] font-bold">WhatsApp</span></td>
                <td className="py-4 px-4"><span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-100 text-[9px] font-bold">{t("statusActive")}</span></td>
                <td className="py-4 px-4"><button className="px-2.5 py-1 rounded bg-white hover:bg-slate-50 border border-slate-200 text-[10px] font-bold text-slate-700 shadow-sm transition-all">{t("actionView")}</button></td>
              </tr>
              <tr className="hover:bg-slate-50 transition-colors">
                <td className="py-4 px-4 font-semibold text-slate-900">Sarah Wijaya</td>
                <td className="py-4 px-4"><span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100 text-[9px] font-bold">Instagram</span></td>
                <td className="py-4 px-4"><span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 text-[9px] font-bold">{t("statusResolved")}</span></td>
                <td className="py-4 px-4"><button className="px-2.5 py-1 rounded bg-white hover:bg-slate-50 border border-slate-200 text-[10px] font-bold text-slate-700 shadow-sm transition-all">{t("actionView")}</button></td>
              </tr>
              <tr className="hover:bg-slate-50 transition-colors">
                <td className="py-4 px-4 font-semibold text-slate-900">Rian Hidayat</td>
                <td className="py-4 px-4"><span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100 text-[9px] font-bold">Web Chat</span></td>
                <td className="py-4 px-4"><span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 text-[9px] font-bold">{t("statusResolved")}</span></td>
                <td className="py-4 px-4"><button className="px-2.5 py-1 rounded bg-white hover:bg-slate-50 border border-slate-200 text-[10px] font-bold text-slate-700 shadow-sm transition-all">{t("actionView")}</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
