"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Navbar from "@/components/Navbar";

export default function ClustersPage() {
  const [hostels, setHostels] = useState<any[]>([]);
  const [activeHostel, setActiveHostel] = useState(0);
  const [activeFloor, setActiveFloor] = useState(0);
  const [selected, setSelected] = useState<string[]>([]); // ordered cluster ids = rank
  const [group, setGroup] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/api/hostels").then((r) => setHostels(r.data));
    api.get("/api/groups/me").then((r) => setGroup(r.data)).catch(() => setGroup(null));
  }, []);

  const hostel = hostels[activeHostel];
  const floor = hostel?.floors?.[activeFloor];

  function toggleCluster(clusterId: string) {
    setSelected((prev) => {
      if (prev.includes(clusterId)) return prev.filter((c) => c !== clusterId);
      if (prev.length >= 5) return prev; // max 5
      return [...prev, clusterId];
    });
  }

  async function submitPreferences() {
    setError("");
    if (selected.length < 3) {
      setError("Please rank at least 3 clusters.");
      return;
    }
    setSubmitting(true);
    try {
      const preferences = selected.map((cluster_id, idx) => ({ cluster_id, rank: idx + 1 }));
      const r = await api.post("/api/booking/preferences", { preferences });
      setResult(r.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not submit preferences");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen">
      <Navbar active="/clusters" />
      <div className="max-w-6xl mx-auto px-6 py-10">
        <h1 className="font-display text-3xl font-semibold mb-1">Cluster map</h1>
        <p className="text-slate mb-6">
          Each cluster is 2 connected rooms sharing a bathroom — 4 seats total. Booking solo? No
          group needed, just rank your preferences below and pay the fee. Click clusters in the
          order you prefer them (3–5 picks). Green = empty, amber = partially filled, grey = full.
        </p>

        {hostels.length > 0 && (
          <>
            <div className="flex gap-3 mb-4 flex-wrap">
              {hostels.map((h, i) => (
                <button
                  key={h.id}
                  onClick={() => { setActiveHostel(i); setActiveFloor(0); }}
                  className={`px-4 py-2 rounded-full text-sm font-medium border ${
                    activeHostel === i ? "bg-marine text-white border-marine" : "border-ink/15 text-slate"
                  }`}
                >
                  {h.name}
                </button>
              ))}
            </div>

            <div className="flex gap-3 mb-6 flex-wrap">
              {hostel?.floors?.map((f: any, i: number) => (
                <button
                  key={f.id}
                  onClick={() => setActiveFloor(i)}
                  className={`px-4 py-2 rounded-full text-sm font-medium border ${
                    activeFloor === i ? "bg-coral text-white border-coral" : "border-ink/15 text-slate"
                  }`}
                >
                  Floor {f.floor_number}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-4 mb-10">
              {floor?.clusters?.map((c: any) => {
                const rankIdx = selected.indexOf(c.id);
                const stateClass =
                  c.state === "empty" ? "room-empty" : c.state === "partial" ? "room-partial" : "room-full";
                return (
                  <button
                    key={c.id}
                    onClick={() => toggleCluster(c.id)}
                    disabled={c.state === "full" && rankIdx === -1}
                    className={`relative border-2 rounded-xl p-3 text-left transition ${stateClass} ${
                      rankIdx !== -1 ? "ring-2 ring-marine" : ""
                    } ${c.state === "full" && rankIdx === -1 ? "opacity-50 cursor-not-allowed" : "hover:-translate-y-0.5"}`}
                  >
                    {rankIdx !== -1 && (
                      <span className="absolute -top-2 -right-2 bg-marine text-white text-xs w-6 h-6 rounded-full flex items-center justify-center font-bold">
                        {rankIdx + 1}
                      </span>
                    )}
                    <p className="text-xs font-semibold text-ink/70 mb-1">Cluster {c.cluster_number}</p>
                    <div className="flex gap-1">
                      {c.rooms.map((r: any) => (
                        <div key={r.id} className="flex-1 bg-white/70 rounded px-1.5 py-1 text-center">
                          <p className="text-[10px] font-bold">Room {r.room_number}</p>
                          <p className="text-[10px] text-slate">{r.occupied_count}/{r.capacity}</p>
                        </div>
                      ))}
                    </div>
                  </button>
                );
              })}
            </div>
          </>
        )}

        <div className="sticky bottom-6 bg-white border border-ink/10 rounded-xl2 shadow-lg p-5 flex items-center justify-between flex-wrap gap-4">
          <div>
            <p className="text-sm font-semibold text-ink">
              {selected.length} cluster{selected.length !== 1 ? "s" : ""} ranked
              {group ? ` · Group size: ${group.members.length}` : ""}
            </p>
            <p className="text-xs text-slate">Pick 3-5 clusters in your order of preference.</p>
          </div>
          <button
            onClick={submitPreferences}
            disabled={submitting || selected.length < 3}
            className="bg-coral text-white rounded-full px-6 py-2.5 font-semibold hover:bg-ink transition disabled:opacity-50"
          >
            {submitting ? "Allocating..." : "Submit preferences"}
          </button>
        </div>

        {error && <p className="text-coral text-sm mt-4">{error}</p>}

        {result && (
          <div className="mt-6 rounded-xl2 p-6 border bg-moss/5 border-moss/30">
            <h3 className="font-display text-lg font-semibold mb-2">Preferences saved</h3>
            <p className="text-sm text-slate">{result.message}</p>
            {result.next_step && <p className="text-sm text-slate mt-1">{result.next_step}</p>}
            <a href="/payment" className="inline-block mt-4 text-marine font-semibold hover:underline">
              Proceed to payment →
            </a>
          </div>
        )}
      </div>
    </main>
  );
}
