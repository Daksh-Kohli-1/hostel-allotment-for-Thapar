"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api, { setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/api/auth/login", { email, password });
      setToken(res.data.access_token);
      if (res.data.role === "admin") {
        router.push("/admin");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-md bg-white rounded-xl2 shadow-md border border-ink/5 p-8">
        <Link href="/" className="font-display text-2xl font-semibold text-ink block mb-8">
          Nest
        </Link>
        <h1 className="font-display text-2xl font-semibold mb-2">Welcome back</h1>
        <p className="text-slate text-sm mb-6">Log in to continue booking your room.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-ink block mb-1">Institute email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-marine"
              placeholder="you@thapar.edu"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-ink block mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-marine"
              placeholder="••••••••"
            />
          </div>
          {error && <p className="text-coral text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-marine text-white rounded-full py-2.5 font-semibold hover:bg-ink transition disabled:opacity-60"
          >
            {loading ? "Logging in..." : "Log in"}
          </button>
        </form>

        <p className="text-sm text-slate mt-6 text-center">
          New here?{" "}
          <Link href="/signup" className="text-marine font-medium hover:underline">
            Create an account
          </Link>
        </p>

        <div className="mt-6 text-xs text-slate bg-sand rounded-lg p-3 leading-relaxed">
          Demo accounts — Student: <b>student1@thapar.edu</b> / Pass@123 · Admin:{" "}
          <b>admin@thapar.edu</b> / Admin@123
        </div>
      </div>
    </main>
  );
}
