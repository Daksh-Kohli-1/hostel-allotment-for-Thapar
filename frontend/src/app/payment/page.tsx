"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Navbar from "@/components/Navbar";

export default function PaymentPage() {
  const [statuses, setStatuses] = useState<any[]>([]);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [allocationMsg, setAllocationMsg] = useState("");

  async function refresh() {
    api.get("/api/auth/me").then((r) => setUser(r.data));
    api.get("/api/payments/status").then((r) => setStatuses(r.data)).catch(() => setStatuses([]));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handlePay() {
    setLoading(true);
    setMessage("");
    setAllocationMsg("");
    try {
      const res = await api.post("/api/payments/pay");
      setMessage(`Payment successful (simulated) — ref ${res.data.transaction_ref}.`);
      if (res.data.allocation?.message) {
        setAllocationMsg(res.data.allocation.message);
      }
      await refresh();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || "Payment could not be completed");
    } finally {
      setLoading(false);
    }
  }

  const myStatus = statuses.find((s) => s.user_id === user?.id);
  const allPaid = statuses.length > 0 && statuses.every((s) => s.status === "paid");

  return (
    <main className="min-h-screen">
      <Navbar active="/payment" />
      <div className="max-w-2xl mx-auto px-6 py-10">
        <h1 className="font-display text-3xl font-semibold mb-1">Hostel fee payment</h1>
        <p className="text-slate mb-2">
          Fee: <span className="font-semibold text-ink">₹60,000</span>. Payments are currently{" "}
          <span className="font-semibold">simulated</span> for testing — a real payment gateway
          will be wired in once the project is accepted.
        </p>
        <p className="text-slate mb-8">
          You don't need to wait for the rest of your group — as soon as your own payment clears,
          you're allotted a room. Group members who join later are added into the same room as
          their payments come in.
        </p>

        <div className="bg-white rounded-xl2 p-6 border border-ink/5 shadow-sm mb-6">
          <h3 className="font-display text-lg font-semibold mb-4">Group payment status</h3>
          {statuses.length === 0 && <p className="text-sm text-slate">No group / booking found yet.</p>}
          <ul className="divide-y divide-ink/10">
            {statuses.map((s) => (
              <li key={s.user_id} className="py-3 flex items-center justify-between">
                <p className="font-medium">{s.name}</p>
                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full ${
                    s.status === "paid" ? "bg-moss/10 text-moss" : "bg-coral/10 text-coral"
                  }`}
                >
                  {s.status}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {allPaid ? (
          <div className="bg-moss/5 border border-moss/30 rounded-xl2 p-6 text-center">
            <p className="font-display text-xl font-semibold text-moss mb-1">Booking confirmed 🎉</p>
            <p className="text-sm text-slate">Every member has paid. Your room is locked in.</p>
          </div>
        ) : (
          <button
            onClick={handlePay}
            disabled={loading || myStatus?.status === "paid"}
            className="w-full bg-coral text-white rounded-full py-3 font-semibold hover:bg-ink transition disabled:opacity-50"
          >
            {myStatus?.status === "paid" ? "You've already paid" : loading ? "Processing..." : "Pay ₹60,000 hostel fee (simulated)"}
          </button>
        )}

        {message && <p className="text-sm text-slate mt-4 text-center">{message}</p>}
        {allocationMsg && <p className="text-sm text-marine font-medium mt-2 text-center">{allocationMsg}</p>}
      </div>
    </main>
  );
}
