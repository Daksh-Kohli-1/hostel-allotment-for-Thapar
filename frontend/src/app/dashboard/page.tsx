"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";
import Navbar from "@/components/Navbar";

export default function Dashboard() {
  const [user, setUser] = useState<any>(null);
  const [group, setGroup] = useState<any>(null);
  const [booking, setBooking] = useState<any>(null);

  useEffect(() => {
    api.get("/api/auth/me").then((r) => setUser(r.data)).catch(() => {});
    api.get("/api/groups/me").then((r) => setGroup(r.data)).catch(() => setGroup(null));
    api.get("/api/booking/status").then((r) => setBooking(r.data)).catch(() => setBooking(null));
  }, []);

  return (
    <main className="min-h-screen">
      <Navbar active="/dashboard" />
      <div className="max-w-6xl mx-auto px-6 py-10">
        <h1 className="font-display text-3xl font-semibold mb-1">
          Welcome{user ? `, ${user.name.split(" ")[0]}` : ""} 👋
        </h1>
        <p className="text-slate mb-8">Here's where things stand with your room booking.</p>

        <div className="grid md:grid-cols-3 gap-5 mb-10">
          <StatusCard
            title="Group"
            value={group ? `Code: ${group.code}` : "No group yet"}
            subtitle={group ? `${group.members.length}/4 members · ${group.status}` : "Create or join one to begin"}
            color="marine"
          />
          <StatusCard
            title="Room booking"
            value={booking ? booking.status : "Not started"}
            subtitle={booking ? `Cluster reserved` : "Submit preferences to allocate"}
            color="coral"
          />
          <StatusCard
            title="Fee payment"
            value={booking && booking.status === "confirmed" ? "All paid" : "Pending"}
            subtitle="Every member must pay to confirm"
            color="moss"
          />
        </div>

        <div className="grid md:grid-cols-3 gap-5">
          <ActionCard
            href="/group"
            title="1. (Optional) Team up"
            body="Want to live with friends? Create a group or join one with a code — up to 4 people. Booking solo needs no group at all."
          />
          <ActionCard
            href="/clusters"
            title="2. Browse & rank clusters"
            body="View the floor-wise visual map, rank 3-5 clusters, and let the allocation engine do the work."
          />
          <ActionCard
            href="/payment"
            title="3. Pay your fee"
            body="Pay the ₹60,000 hostel fee (simulated for now). You're allotted a room the moment your own payment clears — no need to wait on groupmates."
          />
        </div>
      </div>
    </main>
  );
}

function StatusCard({ title, value, subtitle, color }: { title: string; value: string; subtitle: string; color: string }) {
  return (
    <div className="bg-white rounded-xl2 p-6 border border-ink/5 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-slate font-semibold mb-2">{title}</p>
      <p className={`font-display text-xl font-semibold text-${color} mb-1 capitalize`}>{value}</p>
      <p className="text-sm text-slate">{subtitle}</p>
    </div>
  );
}

function ActionCard({ href, title, body }: { href: string; title: string; body: string }) {
  return (
    <Link
      href={href}
      className="block bg-white rounded-xl2 p-6 border border-ink/5 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition"
    >
      <h3 className="font-display text-lg font-semibold text-ink mb-2">{title}</h3>
      <p className="text-sm text-slate leading-relaxed">{body}</p>
    </Link>
  );
}
