import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <header className="flex items-center justify-between px-8 py-6 max-w-6xl mx-auto w-full">
        <div className="font-display text-2xl font-semibold text-ink">Nest</div>
        <nav className="flex gap-3">
          <Link href="/login" className="px-5 py-2 text-marine font-medium hover:underline">
            Log in
          </Link>
          <Link
            href="/signup"
            className="px-5 py-2 bg-marine text-white rounded-full font-medium hover:bg-ink transition"
          >
            Get started
          </Link>
        </nav>
      </header>

      <section className="flex-1 flex flex-col items-center justify-center text-center px-6 max-w-4xl mx-auto">
        <span className="uppercase tracking-widest text-coral text-xs font-semibold mb-4">
          Thapar Hostel Allocation, reimagined
        </span>
        <h1 className="font-display text-5xl md:text-6xl font-semibold text-ink leading-tight mb-6">
          Pick your room.
          <br />
          Pick your people.
        </h1>
        <p className="text-slate text-lg max-w-xl mb-10">
          Form a group, browse the cluster map floor by floor, and lock in the room next to
          your friends — before anyone else does.
        </p>
        <div className="flex gap-4">
          <Link
            href="/signup"
            className="px-8 py-3 bg-coral text-white rounded-full font-semibold text-lg hover:bg-ink transition"
          >
            Start booking
          </Link>
          <Link
            href="/login"
            className="px-8 py-3 border border-ink/20 rounded-full font-semibold text-lg hover:bg-white transition"
          >
            I already have an account
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto px-6 pb-20 w-full">
        {[
          {
            title: "1. Team up (optional)",
            body: "Create a group and share the code, or join a friend's — up to 4 people. Booking solo? No group needed.",
          },
          {
            title: "2. Rank your clusters",
            body: "Browse a floor-wise visual map and rank 3–5 clusters. Live occupancy shown at a glance.",
          },
          {
            title: "3. Pay & confirm",
            body: "Pay your ₹60,000 fee — the moment your own payment clears, you're allotted a room. No waiting on groupmates.",
          },
        ].map((step) => (
          <div key={step.title} className="bg-white rounded-xl2 p-6 shadow-sm border border-ink/5">
            <h3 className="font-display text-xl font-semibold text-marine mb-2">{step.title}</h3>
            <p className="text-slate text-sm leading-relaxed">{step.body}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
