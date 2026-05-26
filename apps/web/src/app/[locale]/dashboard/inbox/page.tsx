"use client";

import React from "react";
import { useTranslations } from "next-intl";

export default function InboxPage() {
  const t = useTranslations("Inbox");

  return (
    <div className="flex h-[calc(100vh-10rem)] border border-slate-200/60 bg-white/60 backdrop-blur-md rounded-2xl overflow-hidden shadow-sm">
      
      {/* 1. Left Contact List (1/3 width) */}
      <div className="w-80 border-r border-slate-200/60 flex flex-col shrink-0 bg-white/40">
        {/* Search bar */}
        <div className="p-4 border-b border-slate-200/60">
          <input
            type="text"
            placeholder={t("searchPlaceholder")}
            className="w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:border-indigo-500 focus:outline-none text-xs text-slate-800"
          />
        </div>
        
        {/* Contacts scrolling list */}
        <div className="flex-1 overflow-y-auto flex flex-col">
          {/* Active Contact */}
          <div className="p-4 bg-indigo-50/50 border-l-2 border-indigo-600 flex justify-between items-start cursor-pointer hover:bg-indigo-50/80 transition-colors">
            <div className="flex gap-3">
              <div className="w-9 h-9 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-xs text-white">
                🟢
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-semibold text-slate-900 truncate">Budi Santoso</span>
                <span className="text-[10px] text-slate-500 truncate max-w-[150px]">Bagaimana cara melakukan retur...</span>
              </div>
            </div>
            <div className="flex flex-col items-end gap-1.5 shrink-0">
              <span className="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-750 text-[8px] font-bold border border-emerald-100">WhatsApp</span>
              <span className="text-[8px] text-slate-400">2m lalu</span>
            </div>
          </div>

          {/* Sample Contact 2 */}
          <div className="p-4 border-b border-slate-100 flex justify-between items-start cursor-pointer hover:bg-slate-50 transition-colors">
            <div className="flex gap-3">
              <div className="w-9 h-9 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-xs text-white">
                🔵
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-semibold text-slate-800 truncate">Sarah Wijaya</span>
                <span className="text-[10px] text-slate-500 truncate max-w-[150px]">Apakah ada promo gratis ongkir...</span>
              </div>
            </div>
            <div className="flex flex-col items-end gap-1.5 shrink-0">
              <span className="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-755 text-[8px] font-bold border border-indigo-100">Instagram</span>
              <span className="text-[8px] text-slate-400">10m lalu</span>
            </div>
          </div>

          {/* Contact 3 */}
          <div className="p-4 border-b border-slate-100 flex justify-between items-start cursor-pointer hover:bg-slate-50 transition-colors">
            <div className="flex gap-3">
              <div className="w-9 h-9 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-xs text-white">
                ⚪
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-semibold text-slate-800 truncate">Rian Hidayat</span>
                <span className="text-[10px] text-slate-500 truncate max-w-[150px]">Agent takeover requested...</span>
              </div>
            </div>
            <div className="flex flex-col items-end gap-1.5 shrink-0">
              <span className="px-1.5 py-0.5 rounded bg-amber-50 text-amber-755 text-[8px] font-bold border border-amber-100">Web Chat</span>
              <span className="text-[8px] text-slate-400">1j lalu</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Middle Message Stream (2/3 width) */}
      <div className="flex-1 flex flex-col min-w-0 bg-white/20">
        {/* Active Contact Header */}
        <div className="p-4 border-b border-slate-200/60 flex justify-between items-center bg-slate-50/50 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-xs">
              👤
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-slate-900">Budi Santoso</span>
              <span className="text-[8px] text-slate-500">ID: budi_santoso_wa_3920</span>
            </div>
          </div>

          {/* Handoff Status Button */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold text-emerald-700 animate-pulse bg-emerald-50 border border-emerald-100 px-2 py-1 rounded-lg">
              {t("activeAI")}
            </span>
            <button className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-755 font-bold text-[10px] text-white shadow-sm transition-colors">
              {t("takeoverButton")}
            </button>
          </div>
        </div>

        {/* Message scroll container */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
          
          {/* User Message */}
          <div className="flex flex-col items-start gap-1 max-w-[70%]">
            <span className="text-[9px] text-slate-400 ml-1">Budi Santoso • 14:10</span>
            <div className="p-3 rounded-2xl rounded-tl-none bg-slate-100 text-slate-800 text-xs leading-relaxed border border-slate-200/60">
              Halo, selamat siang. Saya mau tanya tentang pesanan saya dengan kode INV-83029. Barangnya sampai rusak di pojokan kardusnya. Bagaimana cara melakukan retur ya?
            </div>
          </div>

          {/* AI Response Message */}
          <div className="flex flex-col items-end gap-1 max-w-[70%] self-end">
            <span className="text-[9px] text-slate-400 mr-1">Hiqonis AI Agent • 14:10</span>
            <div className="p-3 rounded-2xl rounded-tr-none bg-indigo-50 text-slate-800 text-xs leading-relaxed border border-indigo-100">
              Halo Kak Budi, selamat siang! Mohon maaf sekali atas ketidaknyamanan yang dialami terkait pesanan kak Budi (INV-83029). 😔
              <br/><br/>
              Kami berkomitmen penuh untuk menjamin kepuasan Anda. Sesuai kebijakan pengembalian Hiqonis, Kakak bisa mengajukan retur gratis dengan syarat:
              <br/>
              1. Foto bagian kardus dan barang yang rusak.
              <br/>
              2. Kirimkan foto tersebut di sini atau klik tautan retur formal.
              <br/><br/>
              Apakah Kakak ingin saya bantu buatkan tiket retur otomatis sekarang?
            </div>
          </div>
        </div>

        {/* Composer Footer */}
        <div className="p-4 border-t border-slate-200/60 bg-slate-50/50 shrink-0">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder={t("chatPlaceholder")}
              className="flex-1 p-3 rounded-xl border border-slate-200 bg-white focus:border-indigo-500 focus:outline-none text-xs text-slate-800"
            />
            <button className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-755 font-bold text-xs text-white shadow-sm transition-colors">
              {t("sendButton")}
            </button>
          </div>
        </div>

      </div>

      {/* 3. Right Context Inspector (1/3 width) */}
      <div className="hidden lg:flex w-64 border-l border-slate-200/60 flex-col p-6 gap-6 overflow-y-auto shrink-0 bg-white/40">
        {/* Customer profile inspect */}
        <div>
          <h4 className="text-xs font-bold text-slate-450 uppercase tracking-wider mb-3">{t("customerDetails")}</h4>
          <div className="flex flex-col gap-2 p-3 rounded-xl border border-slate-200/60 bg-slate-50/50">
            <div className="text-xs font-semibold text-slate-900">Budi Santoso</div>
            <div className="text-[10px] text-slate-500">budi@example.com</div>
            <div className="text-[10px] text-slate-500">+62 812-3456-7890</div>
          </div>
        </div>

        {/* Lead scoring profile inspect */}
        <div>
          <h4 className="text-xs font-bold text-slate-450 uppercase tracking-wider mb-3">{t("leadScoring")}</h4>
          <div className="p-3 rounded-xl border border-slate-200/60 bg-slate-50/50 flex flex-col gap-2">
            <div className="flex justify-between text-[10px]">
              <span className="text-slate-500 font-medium">Score</span>
              <span className="font-bold text-emerald-700">88/100 (Hot Lead)</span>
            </div>
            <div className="w-full bg-slate-200/60 h-1.5 rounded-full overflow-hidden shadow-inner">
              <div className="bg-emerald-500 h-full w-[88%]" />
            </div>
            <span className="text-[9px] text-slate-500 leading-relaxed mt-1">
              Ketertarikan tinggi pada retur pelayanan, potensi retensi pelanggan optimal.
            </span>
          </div>
        </div>

        {/* Knowledge Base lookup inspect */}
        <div>
          <h4 className="text-xs font-bold text-slate-450 uppercase tracking-wider mb-3">{t("kbReference")}</h4>
          <div className="flex flex-col gap-2">
            <div className="p-2.5 rounded-lg border border-slate-200 bg-white text-[10px] hover:border-indigo-500/30 cursor-pointer shadow-sm">
              <div className="font-semibold text-slate-800">Kebijakan Retur & Refund</div>
              <div className="text-slate-500 mt-1">{t("semanticMatch")}: 94.2%</div>
            </div>
            <div className="p-2.5 rounded-lg border border-slate-200 bg-white text-[10px] hover:border-indigo-500/30 cursor-pointer shadow-sm">
              <div className="font-semibold text-slate-800">Penanganan Klaim Kerusakan</div>
              <div className="text-slate-500 mt-1">{t("semanticMatch")}: 81.5%</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
