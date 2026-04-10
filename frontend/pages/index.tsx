import Head from "next/head";
import Link from "next/link";

const literature = [
  "Blockchain in Healthcare: Ekblaw et al. (2016) MedRec, Azaria et al. (2016), Peterson et al. (2016)",
  "Medical Data Security: HIPAA Security Rule, Fernandez-Aleman et al. (2013), Kruse et al. (2017)",
  "Access Control Systems: Zhang and Liu (2010) RBAC, Hu et al. (2014) ABAC, Xiao et al. (2013)",
];

const problemPoints = [
  "Unauthorized access to records without patient knowledge",
  "No reliable audit trail of who accessed data and when",
  "Emergency delays while critical records are requested",
];

const features = [
  {
    title: "Tamper-Proof Access",
    description:
      "Every access attempt is permanently recorded on-chain, creating an immutable audit trail.",
  },
  {
    title: "Complete Transparency",
    description:
      "Patients can view who accessed their records, when access happened, and under what authorization.",
  },
  {
    title: "Smart Access Key Management",
    description:
      "Permanent cryptographic keys for authorized providers and temporary keys for emergencies.",
  },
];

const workflow = [
  "Admin registers patient with wallet",
  "Doctor requests access keys",
  "Smart contract issues cryptographic keys",
  "Doctor accesses records with key",
  "All activity is logged on blockchain",
  "Patient audits complete history",
];

const architecture = [
  {
    layer: "Frontend",
    stack: "Next.js 16, TypeScript, TailwindCSS, Zustand, Docker (Node 18-alpine)",
  },
  {
    layer: "Backend",
    stack: "FastAPI, SQLAlchemy, Supabase, JWT and cryptography security layer",
  },
  {
    layer: "Blockchain",
    stack: "Ganache CLI, Web3.py, Healthlogger.sol (Ethereum-compatible)",
  },
];

const emergencyFlow = [
  "Emergency responders request temporary access",
  "Smart contract generates a time-limited key (for example 24 hours)",
  "Access expires automatically after the allowed duration",
  "All emergency access is logged on-chain",
  "Patient is notified of the emergency access event",
];

const roadmap = [
  "Real-Time Monitoring: Connected wearables and medical IoT devices",
  "Prescription Tracking: Blockchain-based medication history management",
  "Biometric Auth: Aadhaar integration for secure identity verification",
];

export default function HomePage() {
  return (
    <>
      <Head>
        <title>SecureMedi | Decentralized Healthcare Access</title>
        <meta
          name="description"
          content="SecureMedi is a decentralized patient platform for secure, auditable healthcare data access with emergency protocols."
        />
      </Head>

      <main className="min-h-screen bg-slate-950 text-slate-100">
        <section className="relative overflow-hidden border-b border-cyan-900/40">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(6,182,212,0.25),transparent_35%),radial-gradient(circle_at_80%_10%,rgba(16,185,129,0.25),transparent_30%),linear-gradient(120deg,#020617_0%,#0f172a_40%,#052e2b_100%)]" />
          <div className="relative mx-auto max-w-6xl px-4 py-24 sm:px-6 lg:px-8 lg:py-28">
            <p className="inline-flex rounded-full border border-cyan-500/40 bg-cyan-400/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">
              Decentralized Healthcare Access
            </p>
            <h1 className="mt-6 max-w-3xl text-5xl font-black leading-tight text-white sm:text-6xl">
              SecureMedi
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-relaxed text-slate-200 sm:text-xl">
              A decentralized patient platform giving patients complete control over
              their medical data with secure, auditable access for healthcare
              providers.
            </p>
            <p className="mt-4 text-sm uppercase tracking-widest text-cyan-100/80">
              Neel Butala | Arnav Anand | Jayesh Dhoot
            </p>

            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                href="/login"
                className="rounded-lg bg-cyan-400 px-6 py-3 text-sm font-bold uppercase tracking-wide text-slate-950 transition hover:bg-cyan-300"
              >
                Open User Portal
              </Link>
              <Link
                href="/admin"
                className="rounded-lg border border-emerald-300/50 bg-emerald-300/10 px-6 py-3 text-sm font-bold uppercase tracking-wide text-emerald-100 transition hover:bg-emerald-300/20"
              >
                Open Admin Dashboard
              </Link>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl space-y-16 px-4 py-16 sm:px-6 lg:px-8">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">Literature Review</h2>
            <p className="mt-2 text-sm uppercase tracking-[0.18em] text-cyan-300">Research Foundation</p>
            <div className="mt-6 grid gap-3">
              {literature.map((entry, index) => (
                <div key={index} className="rounded-lg border border-slate-700 bg-slate-900 p-4 text-sm text-slate-200">
                  {entry}
                </div>
              ))}
            </div>
            <div className="mt-4 rounded-lg border border-amber-500/40 bg-amber-500/10 p-4 text-sm text-amber-100">
              Key Gap: Existing solutions lack emergency access protocols with automatic expiration and comprehensive tamper-proof audit trails.
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 sm:p-8">
              <h2 className="text-2xl font-bold text-white">The Problem</h2>
              <p className="mt-2 text-sm uppercase tracking-[0.18em] text-cyan-300">Critical Gaps in Data Security</p>
              <ul className="mt-6 space-y-3 text-sm text-slate-200">
                {problemPoints.map((point, index) => (
                  <li key={index} className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-3">
                    {point}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 sm:p-8">
              <h2 className="text-2xl font-bold text-white">Data Breach Trends</h2>
              <p className="mt-2 text-sm uppercase tracking-[0.18em] text-cyan-300">2019 to 2023</p>
              <div className="mt-6 grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-center">
                  <p className="text-3xl font-black text-red-300">200%</p>
                  <p className="mt-1 text-xs uppercase tracking-widest text-red-100">Growth in Breaches</p>
                </div>
                <div className="rounded-lg border border-orange-500/30 bg-orange-500/10 p-4 text-center">
                  <p className="text-3xl font-black text-orange-300">150%</p>
                  <p className="mt-1 text-xs uppercase tracking-widest text-orange-100">Increase in Impact</p>
                </div>
              </div>
              <p className="mt-4 text-sm leading-relaxed text-slate-300">
                Breach incidents and affected individuals continue to rise, increasing financial loss, legal exposure, and trust breakdown in traditional systems.
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-cyan-700/30 bg-cyan-500/10 p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">Solution: What Is SecureMedi?</h2>
            <p className="mt-4 text-slate-100">
              A decentralized patient platform that gives patients complete control over their medical data while ensuring secure, auditable access for healthcare providers.
            </p>
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-lg border border-cyan-400/30 bg-slate-900/70 p-4">
                <p className="text-xs uppercase tracking-widest text-cyan-200">Patient Ownership</p>
                <p className="mt-2 text-sm text-slate-200">Full control over who accesses records.</p>
              </div>
              <div className="rounded-lg border border-cyan-400/30 bg-slate-900/70 p-4">
                <p className="text-xs uppercase tracking-widest text-cyan-200">Transparency</p>
                <p className="mt-2 text-sm text-slate-200">Visibility into every access event.</p>
              </div>
              <div className="rounded-lg border border-cyan-400/30 bg-slate-900/70 p-4">
                <p className="text-xs uppercase tracking-widest text-cyan-200">Trust</p>
                <p className="mt-2 text-sm text-slate-200">Immutable blockchain-backed audit trails.</p>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white sm:text-3xl">Key Features</h2>
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              {features.map((feature, index) => (
                <div key={index} className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
                  <h3 className="text-lg font-semibold text-cyan-200">{feature.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-slate-300">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white sm:text-3xl">Technical Architecture</h2>
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              {architecture.map((item, index) => (
                <div key={index} className="rounded-xl border border-emerald-600/30 bg-emerald-500/10 p-5">
                  <p className="text-xs uppercase tracking-widest text-emerald-200">{item.layer}</p>
                  <p className="mt-3 text-sm leading-relaxed text-slate-100">{item.stack}</p>
                </div>
              ))}
            </div>
            <p className="mt-4 text-sm text-slate-300">
              Orchestration and DevOps: Docker Compose with automated deployment via compile_and_deploy.py.
            </p>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white sm:text-3xl">How It Works</h2>
            <p className="mt-2 text-sm text-slate-300">
              From patient registration through key generation, on-chain logging, and patient audit, every step is secured and transparent.
            </p>
            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {workflow.map((step, index) => (
                <div key={index} className="rounded-lg border border-slate-800 bg-slate-900 p-4 text-sm text-slate-200">
                  <span className="mr-2 inline-block rounded bg-cyan-400 px-2 py-0.5 text-xs font-bold text-slate-950">{index + 1}</span>
                  {step}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-amber-500/40 bg-amber-500/10 p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">Emergency Access Feature</h2>
            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <div>
                <p className="text-sm uppercase tracking-[0.18em] text-amber-200">How It Works</p>
                <ul className="mt-3 space-y-2 text-sm text-slate-100">
                  {emergencyFlow.map((step, index) => (
                    <li key={index} className="rounded-lg border border-amber-300/30 bg-slate-900/70 px-4 py-3">
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.18em] text-amber-200">Benefits</p>
                <ul className="mt-3 space-y-2 text-sm text-slate-100">
                  <li className="rounded-lg border border-amber-300/30 bg-slate-900/70 px-4 py-3">Immediate access in life-threatening situations</li>
                  <li className="rounded-lg border border-amber-300/30 bg-slate-900/70 px-4 py-3">No permanent access granted</li>
                  <li className="rounded-lg border border-amber-300/30 bg-slate-900/70 px-4 py-3">Automatic security restoration</li>
                  <li className="rounded-lg border border-amber-300/30 bg-slate-900/70 px-4 py-3">Complete audit trail maintained</li>
                  <li className="rounded-lg border border-amber-300/30 bg-slate-900/70 px-4 py-3">Patient privacy protected long-term</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">Roadmap and Benefits</h2>
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              {roadmap.map((item, index) => (
                <div key={index} className="rounded-lg border border-slate-700 bg-slate-900 p-4 text-sm text-slate-200">
                  {item}
                </div>
              ))}
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 p-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-100">Patients</h3>
                <p className="mt-2 text-sm text-slate-100">Complete transparency, data control, and privacy.</p>
              </div>
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-100">Providers</h3>
                <p className="mt-2 text-sm text-slate-100">Streamlined secure access with emergency protocols.</p>
              </div>
              <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-amber-100">Healthcare Systems</h3>
                <p className="mt-2 text-sm text-slate-100">Enhanced security, reduced breaches, and compliance support.</p>
              </div>
            </div>
          </div>
        </section>

        <footer className="border-t border-slate-800 bg-slate-950 py-10">
          <div className="mx-auto max-w-6xl px-4 text-center sm:px-6 lg:px-8">
            <p className="text-xl font-bold uppercase tracking-[0.2em] text-cyan-200">Thank You</p>
            <p className="mt-3 text-sm text-slate-300">
              Jayesh Dhoot (2427030072) | Neel Butala (2427030157) | Arnav Anand (2427030154)
            </p>
            <p className="mt-3 text-xs text-slate-400">SecureMedi {new Date().getFullYear()}</p>
          </div>
        </footer>
      </main>
    </>
  );
}
