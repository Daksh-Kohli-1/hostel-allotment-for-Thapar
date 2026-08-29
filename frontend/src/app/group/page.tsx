"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Navbar from "@/components/Navbar";

export default function GroupPage() {
  const [group, setGroup] = useState<any>(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function refresh() {
    try {
      const r = await api.get("/api/groups/me");
      setGroup(r.data);
    } catch {
      setGroup(null);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function createGroup() {
    setLoading(true);
    setError("");
    try {
      await api.post("/api/groups/create");
      await refresh();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not create group");
    } finally {
      setLoading(false);
    }
  }

  async function joinGroup(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.post("/api/groups/join", { code });
      await refresh();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not join group");
    } finally {
      setLoading(false);
    }
  }

  async function leaveGroup() {
    setLoading(true);
    try {
      await api.delete("/api/groups/leave");
      await refresh();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not leave group");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen">
      <Navbar active="/group" />
      <div className="max-w-3xl mx-auto px-6 py-10">
        <h1 className="font-display text-3xl font-semibold mb-1">Your group</h1>
        <p className="text-slate mb-8">
          Teaming up is optional — groups can be 1 to 4 members. Booking solo? Skip this page
          entirely and go straight to the cluster map; a group of one is created for you
          automatically. Group leaders pick the cluster on behalf of everyone, and each member is
          allotted a seat as soon as their own fee payment clears.
        </p>

        {!group && (
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl2 p-6 border border-ink/5 shadow-sm">
              <h3 className="font-display text-lg font-semibold mb-2">Create a group</h3>
              <p className="text-sm text-slate mb-4">
                You'll become the group leader and get a shareable code. Solo? A 1-person group works too — you'll be placed as a flexible single.
              </p>
              <button
                onClick={createGroup}
                disabled={loading}
                className="bg-marine text-white rounded-full px-6 py-2.5 font-semibold hover:bg-ink transition disabled:opacity-60"
              >
                Create group
              </button>
            </div>
            <div className="bg-white rounded-xl2 p-6 border border-ink/5 shadow-sm">
              <h3 className="font-display text-lg font-semibold mb-2">Join a group</h3>
              <form onSubmit={joinGroup} className="flex gap-2">
                <input
                  value={code}
                  onChange={(e) => setCode(e.target.value.toUpperCase())}
                  placeholder="Enter code"
                  className="flex-1 border border-ink/15 rounded-lg px-4 py-2.5"
                />
                <button
                  disabled={loading}
                  className="bg-coral text-white rounded-full px-5 py-2.5 font-semibold hover:bg-ink transition disabled:opacity-60"
                >
                  Join
                </button>
              </form>
            </div>
          </div>
        )}

        {group && (
          <div className="bg-white rounded-xl2 p-6 border border-ink/5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate font-semibold">Group code</p>
                <p className="font-display text-2xl font-semibold text-marine">{group.code}</p>
              </div>
              <span className="px-3 py-1 rounded-full bg-sand text-ink text-sm font-medium capitalize">
                {group.status.replace("_", " ")}
              </span>
            </div>

            <p className="text-sm text-slate mb-3">{group.members.length} / 4 members</p>
            <ul className="divide-y divide-ink/10 mb-6">
              {group.members.map((m: any) => (
                <li key={m.id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium">{m.name}</p>
                    <p className="text-xs text-slate">{m.roll_no}</p>
                  </div>
                  <span
                    className={`text-xs font-semibold px-2 py-1 rounded-full ${
                      m.payment_status === "paid" ? "bg-moss/10 text-moss" : "bg-coral/10 text-coral"
                    }`}
                  >
                    {m.payment_status}
                  </span>
                </li>
              ))}
            </ul>

            {group.status === "forming" && (
              <button
                onClick={leaveGroup}
                disabled={loading}
                className="text-sm text-coral font-medium hover:underline"
              >
                Leave group
              </button>
            )}

            {group.status === "forming" && (
              <div className="mt-6 bg-sand rounded-lg p-4 text-sm text-slate">
                Once your group is ready, head to the{" "}
                <a href="/clusters" className="text-marine font-semibold hover:underline">
                  cluster map
                </a>{" "}
                to rank your preferences.
              </div>
            )}
          </div>
        )}

        {error && <p className="text-coral text-sm mt-4">{error}</p>}
      </div>
    </main>
  );
}
