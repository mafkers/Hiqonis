import React from "react";
import { Link } from "@/i18n/routing";
import { getTranslations } from "next-intl/server";

export default async function DashboardLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Sidebar" });

  return (
    <div className="relative min-h-screen flex bg-slate-50 text-slate-900 overflow-hidden">
      {/* Background gradients */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-64 border-r border-slate-200/60 bg-white/80 backdrop-blur-xl p-6 justify-between shrink-0">
        <div className="flex flex-col gap-8">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-md shadow-indigo-500/10">
              <span className="font-bold text-sm tracking-wider text-white">H</span>
            </div>
            <span className="font-bold text-lg bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-600 bg-clip-text text-transparent tracking-tight">
              Hiqonis
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex flex-col gap-1.5">
            <Link
              href="/dashboard"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 bg-indigo-50 text-indigo-600 border border-indigo-100"
            >
              <span>📊</span> {t("overview")}
            </Link>
            <Link
              href="/dashboard/inbox"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
            >
              <span>📥</span> {t("inbox")}
            </Link>
            <Link
              href="/dashboard/agents"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
            >
              <span>🤖</span> {t("agents")}
            </Link>
            <Link
              href="/dashboard/knowledge"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
            >
              <span>📚</span> {t("knowledge")}
            </Link>
            <Link
              href="/dashboard/crm"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
            >
              <span>👥</span> {t("crm")}
            </Link>
            <Link
              href="/dashboard/settings"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
            >
              <span>⚙️</span> {t("settings")}
            </Link>
          </nav>
        </div>

        {/* User Card */}
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 backdrop-blur-md flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-xs text-white shadow-sm shadow-indigo-500/10">
            MS
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-semibold text-slate-800 truncate">Momo Solo</span>
            <span className="text-[10px] text-slate-500 truncate">{t("admin")}</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 border-b border-slate-200/60 bg-white/60 backdrop-blur-md px-6 py-4 flex justify-between items-center shrink-0">
          <h2 className="text-base font-semibold text-slate-800">Hiqonis Console</h2>
          
          <div className="flex items-center gap-4">
            {/* Locale Toggle */}
            <div className="flex items-center gap-1 bg-white border border-slate-200 p-0.5 rounded-lg text-[10px] shadow-sm">
              <Link href="/dashboard" locale="id" className="px-2 py-1 rounded text-slate-500 hover:text-slate-900 transition-colors">ID</Link>
              <Link href="/dashboard" locale="en" className="px-2 py-1 rounded text-slate-500 hover:text-slate-900 transition-colors">EN</Link>
            </div>

            <div className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center text-xs font-medium cursor-pointer hover:bg-slate-50 transition-colors shadow-sm">
              🔔
            </div>
          </div>
        </header>

        {/* Page Children */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
