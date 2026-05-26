"use client";

import React, { useState } from "react";
import { Link } from "@/i18n/routing";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

export default function SignupPage() {
  const t = useTranslations("Signup");
  const router = useRouter();
  const [companyName, setCompanyName] = useState("");
  const [adminName, setAdminName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    const steps = [
      t("step1"),
      t("step2"),
      t("step3"),
      t("step4"),
      t("step5")
    ];

    let currentStep = 0;
    setStatusText(steps[0]);

    const interval = setInterval(() => {
      currentStep++;
      if (currentStep < steps.length) {
        setStatusText(steps[currentStep]);
      } else {
        clearInterval(interval);
        setLoading(false);
        router.push("/dashboard");
      }
    }, 600);
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

      {/* Signup Card */}
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

        {loading ? (
          /* Multi-Tenant Provisioning Loader */
          <div className="py-12 flex flex-col items-center justify-center gap-6 text-center">
            <div className="w-12 h-12 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin" />
            <div className="flex flex-col gap-2">
              <span className="text-sm font-semibold text-slate-800">{t("loaderTitle")}</span>
              <span className="text-xs text-indigo-600 font-medium animate-pulse">{statusText}</span>
            </div>
          </div>
        ) : (
          /* Onboarding Form */
          <form onSubmit={handleSignup} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                {t("companyLabel")}
              </label>
              <input
                type="text"
                required
                placeholder="PT Sukses Bersama"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white text-slate-800 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/10 transition-all duration-200"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                {t("adminLabel")}
              </label>
              <input
                type="text"
                required
                placeholder="Momo Solo"
                value={adminName}
                onChange={(e) => setAdminName(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white text-slate-800 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/10 transition-all duration-200"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                {t("emailLabel")}
              </label>
              <input
                type="email"
                required
                placeholder="momo@sukses.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white text-slate-800 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/10 transition-all duration-200"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                {t("passwordLabel")}
              </label>
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
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 font-bold text-sm text-white shadow-md shadow-indigo-500/10 hover:shadow-lg hover:shadow-indigo-500/20 hover:scale-[1.01] active:scale-[0.99] transition-all duration-300 mt-2"
            >
              {t("signupButton")}
            </button>
          </form>
        )}

        {/* Links */}
        {!loading && (
          <div className="flex flex-col gap-3 text-center mt-2 text-xs">
            <span className="text-slate-600">
              {t("haveAccount")}{" "}
              <Link href="/login" className="text-indigo-600 font-semibold hover:underline">
                {t("signInLink")}
              </Link>
            </span>
            <Link
              href="/"
              className="text-slate-500 hover:text-slate-700 transition-colors"
            >
              {t("backLink")}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
