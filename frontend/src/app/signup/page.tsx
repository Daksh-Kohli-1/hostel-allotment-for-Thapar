"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api, { setToken } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    name: "",
    roll_no: "",
    email: "",
    password: "",
    gender: "male",
    year: 2,
    branch: "",
    contact: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(field: string, value: any) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/api/auth/signup", form);
      setToken(res.data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6 py-10">
      <div className="w-full max-w-lg bg-white rounded-xl2 shadow-md border border-ink/5 p-8">
        <Link href="/" className="font-display text-2xl font-semibold text-ink block mb-6">
          Nest
        </Link>
        <h1 className="font-display text-2xl font-semibold mb-2">Create your account</h1>
        <p className="text-slate text-sm mb-6">Set up your profile to start forming a group.</p>

        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="text-sm font-medium block mb-1">Full name</label>
            <input required value={form.name} onChange={(e) => update("name", e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Roll number</label>
            <input required value={form.roll_no} onChange={(e) => update("roll_no", e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Year</label>
            <select value={form.year} onChange={(e) => update("year", Number(e.target.value))}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5">
              {[1, 2, 3, 4].map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          <div className="col-span-2">
            <label className="text-sm font-medium block mb-1">Institute email</label>
            <input type="email" required value={form.email} onChange={(e) => update("email", e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5" placeholder="you@thapar.edu" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Branch</label>
            <input required value={form.branch} onChange={(e) => update("branch", e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Gender</label>
            <select value={form.gender} onChange={(e) => update("gender", e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5">
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Contact</label>
            <input required value={form.contact} onChange={(e) => update("contact", e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Password</label>
            <input type="password" required value={form.password} onChange={(e) => update("password", e.target.value)}
              className="w-full border border-ink/15 rounded-lg px-4 py-2.5" />
          </div>

          {error && <p className="text-coral text-sm col-span-2">{error}</p>}

          <button type="submit" disabled={loading}
            className="col-span-2 bg-coral text-white rounded-full py-2.5 font-semibold hover:bg-ink transition disabled:opacity-60">
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-sm text-slate mt-6 text-center">
          Already registered?{" "}
          <Link href="/login" className="text-marine font-medium hover:underline">Log in</Link>
        </p>
      </div>
    </main>
  );
}
