"use client";

import React, { useState } from "react";
import { useTranslations } from "next-intl";

export default function SettingsPage() {
  const t = useTranslations("Settings");
  const [backingUp, setBackingUp] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  const handleBackup = () => {
    setBackingUp(true);
    setSuccessMsg("");
    setTimeout(() => {
      setBackingUp(false);
      setSuccessMsg(t("backupSuccess"));
    }, 1500);
  };

  return (
    <div className="flex flex-col gap-8 max-w-4xl text-slate-800">
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

      {/* Profile Settings Card */}
      <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-6">
        <h3 className="font-bold text-lg text-slate-900 border-b border-slate-200 pb-3 flex items-center gap-2">
          <span>👤</span> {t("tenantProfile")}
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold text-slate-500 uppercase">Nama Organisasi</label>
            <input
              type="text"
              defaultValue="Hiqonis Testing"
              className="p-3 rounded-xl border border-slate-200 bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/10 focus:outline-none text-sm text-slate-800 transition-all"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold text-slate-500 uppercase">Domain</label>
            <input
              type="text"
              defaultValue="hiqonis.com"
              className="p-3 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-400 cursor-not-allowed transition-all"
              disabled
            />
          </div>
        </div>
      </div>

      {/* Webhook Configuration Card */}
      <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-6">
        <h3 className="font-bold text-lg text-slate-900 border-b border-slate-200 pb-3 flex items-center gap-2">
          <span>🔗</span> {t("webhookTitle")}
        </h3>

        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold text-slate-500 uppercase">Webhook Target URL</label>
            <input
              type="url"
              defaultValue="https://api.myclient.com/v1/webhooks/hiqonis"
              className="p-3 rounded-xl border border-slate-200 bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/10 focus:outline-none text-sm text-slate-800 transition-all"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold text-slate-500 uppercase">{t("webhookSecret")}</label>
            <input
              type="text"
              defaultValue="whsec_dummy_signing_secret_for_demo_purposes_only_123456"
              className="p-3 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-400 cursor-not-allowed font-mono text-xs transition-all"
              disabled
            />
          </div>
        </div>
      </div>

      {/* Disaster Recovery Card */}
      <div className="p-6 rounded-2xl border border-slate-200/60 bg-white shadow-sm flex flex-col gap-6">
        <h3 className="font-bold text-lg text-slate-900 border-b border-slate-200 pb-3 flex items-center gap-2">
          <span>💾</span> {t("disasterRecovery")}
        </h3>

        <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex flex-col">
            <span className="text-xs font-bold text-indigo-750 tracking-wide uppercase">Database Auto-Backup</span>
            <span className="text-[10px] text-slate-600 mt-1 max-w-sm">
              Trigger backup database lokal asinkron. Berkas salinan (.sql.gz) akan otomatis dirotasikan secara teratur.
            </span>
          </div>
          <button 
            onClick={handleBackup}
            disabled={backingUp}
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:scale-[1.01] active:scale-[0.99] font-bold text-xs text-white shadow-md shadow-indigo-500/10 transition-all disabled:opacity-50"
          >
            {backingUp ? t("backingUp") : t("backupButton")}
          </button>
        </div>
      </div>
    </div>
  );
}
