"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { clearToken } from "@/lib/api";

export default function Navbar({ active }: { active?: string }) {
  const router = useRouter();

  function logout() {
    clearToken();
    router.push("/login");
  }

  const links = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/clusters", label: "Cluster map" },
    { href: "/group", label: "My group" },
    { href: "/payment", label: "Payment" },
  ];

  return (
    <header className="border-b border-ink/10 bg-white sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard" className="font-display text-xl font-semibold text-ink">
          Nest
        </Link>
        <nav className="hidden md:flex gap-6">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`text-sm font-medium ${
                active === l.href ? "text-marine" : "text-slate hover:text-ink"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <button
          onClick={logout}
          className="text-sm font-medium text-slate hover:text-coral"
        >
          Log out
        </button>
      </div>
    </header>
  );
}
