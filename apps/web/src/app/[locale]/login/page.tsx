"use client";

import React, { useState } from "react";
import { Link } from "@/i18n/routing";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

export default function LoginPage() {
  const t = useTranslations("Login");
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    setTimeout(() => {
      setLoading(false);
      router.push("/dashboard");
    }, 800);
  };

  const handleSSOSignIn = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      router.push("/dashboard");
    }, 1200);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background gradients */}
      <div className="absolute inset-0 -z-10 bg-slate-50">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
        {/* Subtle grid pattern overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-40" />
      </div>

      {/* Login Card */}
      <div className="w-full max-w-md p-8 rounded-3xl border border-slate-200 bg-white/80 backdrop-blur-xl shadow-xl shadow-indigo-500/5 flex flex-col gap-6">
        {/* Brand logo */}
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-md shadow-indigo-500/20">
            <span className="font-bold text-xl tracking-wider text-white">H</span>
          </div>
          <h2 className="font-extrabold text-3xl tracking-tight text-slate-900 mt-2">
            {t("title")}
          </h2>
          <p className="text-slate-500 text-xs tracking-wide">
            {t("subtitle")}
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-xl border border-red-200 bg-red-50 text-red-600 text-xs font-medium text-center">
            {error}
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSignIn} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
              {t("emailLabel")}
            </label>
            <input
              type="text"
              required
              placeholder="admin@hiqonis.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white text-slate-800 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/10 transition-all duration-200"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between items-center">
              <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                {t("passwordLabel")}
              </label>
              <a href="#" className="text-[10px] text-indigo-600 font-semibold hover:underline">
                {t("forgotPassword")}
              </a>
            </div>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white text-slate-800 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/10 transition-all duration-200"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 font-bold text-sm text-white shadow-md shadow-indigo-500/10 hover:shadow-lg hover:shadow-indigo-500/20 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:scale-100 transition-all duration-300 mt-2"
          >
            {loading ? t("signingIn") : t("signInButton")}
          </button>
        </form>

        {/* Divider */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-[1px] bg-slate-200" />
          <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider shrink-0">
            {t("ssoDivider")}
          </span>
          <div className="flex-1 h-[1px] bg-slate-200" />
        </div>

        {/* Enterprise SSO Buttons */}
        <div className="flex flex-col gap-2.5">
          <button
            onClick={handleSSOSignIn}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 font-semibold text-xs text-slate-700 flex items-center justify-center gap-2.5 shadow-sm transition-all duration-300"
          >
            <span>🛡️</span> {t("samlButton")}
          </button>
          <button
            onClick={handleSSOSignIn}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 font-semibold text-xs text-slate-700 flex items-center justify-center gap-2.5 shadow-sm transition-all duration-300"
          >
            <span className="text-sm">🔑</span> {t("oidcButton")}
          </button>
        </div>

        {/* Back Link & Signup */}
        <div className="flex flex-col gap-3 text-center mt-2 text-xs">
          <span className="text-slate-600">
            {t("noAccount")}{" "}
            <Link href="/signup" className="text-indigo-600 font-semibold hover:underline">
              {t("registerLink")}
            </Link>
          </span>
          <Link
            href="/"
            className="text-xs text-slate-500 hover:text-slate-700 transition-colors"
          >
            {t("backLink")}
          </Link>
        </div>
      </div>
    </div>
  );
}
