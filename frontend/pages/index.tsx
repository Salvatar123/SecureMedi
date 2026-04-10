import Head from "next/head";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <>
        <Head>
          <title>SecureMedi - Blockchain Healthcare Platform</title>
        </Head>
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-purple-100 flex items-center justify-center p-4">
          <div className="text-center">
            <div className="inline-block p-4 bg-gradient-to-br from-purple-600 to-violet-600 rounded-2xl mb-6 animate-pulse">
              <div className="text-white text-4xl font-bold">SM</div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">SecureMedi</h1>
            <p className="text-gray-700 mb-8">Loading blockchain healthcare platform...</p>
            <div className="w-64 h-1 bg-purple-200 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-purple-600 to-violet-600 animate-pulse" style={{width: '35%'}}></div>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>SecureMedi - Blockchain Healthcare Platform</title>
        <meta name="description" content="Decentralized healthcare platform with blockchain-powered access control and emergency protocols" />
      </Head>

      <main className="min-h-screen bg-purple-50">
        {/* Hero Section */}
        <section className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-purple-100 flex items-center justify-center px-4 py-16">
          <div className="max-w-4xl text-center">
            <div className="inline-block mb-6">
              <div className="inline-block p-3 bg-gradient-to-br from-purple-600 to-violet-600 rounded-xl mb-4">
                <span className="text-white font-bold text-2xl">SM</span>
              </div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent mb-6">
              SecureMedi
            </h1>
            <p className="text-xl text-gray-800 mb-4 max-w-2xl mx-auto">
              Blockchain Healthcare Access Control with Emergency Protocols
            </p>
            <p className="text-gray-700 mb-8 max-w-2xl mx-auto leading-relaxed">
              A decentralized platform that gives patients complete control over their medical data while ensuring secure, auditable access for healthcare providers.
            </p>
            <p className="text-sm text-gray-700 mb-8">
              Team: Neel Butala • Arnav Anand • Jayesh Dhoot
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link href="/admin" className="px-8 py-3 bg-gradient-to-r from-purple-600 to-violet-600 text-white font-semibold rounded-lg hover:shadow-lg transform hover:scale-105 transition-all duration-200">
                Admin Dashboard
              </Link>
              <Link href="/login" className="px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold rounded-lg hover:shadow-lg transform hover:scale-105 transition-all duration-200">
                User Portal
              </Link>
            </div>
          </div>
        </section>

        {/* Content Sections */}
        <section className="py-20 px-4 max-w-6xl mx-auto">
          {/* The Problem */}
          <div className="grid md:grid-cols-3 gap-6 mb-20">
            <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">The Problem</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="mr-3 text-red-500">⚠</span>
                  <span>Unauthorized access without patient knowledge</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-3 text-red-500">⚠</span>
                  <span>No audit trail for data access tracking</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-3 text-red-500">⚠</span>
                  <span>Critical emergency access delays</span>
                </li>
              </ul>
            </div>

            <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Data Breaches</h3>
              <div className="space-y-2 text-gray-700">
                <p className="text-sm">📊 <strong>200%</strong> growth from 2019-2023</p>
                <p className="text-sm">📈 <strong>150%</strong> increase in affected individuals</p>
                <p className="text-sm">💰 Growing financial and legal risks</p>
                <p className="text-xs text-gray-500 mt-4">Traditional systems are failing to protect patient data at scale.</p>
              </div>
            </div>

            <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Our Solution</h3>
              <p className="text-gray-700 mb-4">
                SecureMedi gives patients ownership, transparency, and trust over their medical data through blockchain-backed access control.
              </p>
              <p className="text-sm text-gray-500">Immutable audit trails. Zero unauthorized access. Peace of mind.</p>
            </div>
          </div>

          {/* Key Features */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Key Features</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
                <div className="text-3xl mb-3">🔒</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Tamper-Proof Access</h3>
                <p className="text-gray-700">Every access attempt is permanently recorded on blockchain, creating an immutable audit trail that cannot be altered.</p>
              </div>
              <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
                <div className="text-3xl mb-3">👁</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Complete Transparency</h3>
                <p className="text-gray-700">Patients view their complete access history including who accessed their records, when, and the authorization level.</p>
              </div>
              <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
                <div className="text-3xl mb-3">🔑</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Access Keys</h3>
                <p className="text-gray-700">Cryptographic access keys for authorized providers (permanent) and emergency responders (temporary with expiry).</p>
              </div>
            </div>
          </div>

          {/* How It Works */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">How It Works</h2>
            <div className="grid md:grid-cols-6 gap-3">
              {[
                { num: '1', title: 'Registration', desc: 'Blockchain wallets' },
                { num: '2', title: 'Authentication', desc: 'Provider login' },
                { num: '3', title: 'Key Generation', desc: 'Crypto keys' },
                { num: '4', title: 'Data Access', desc: 'Secure request' },
                { num: '5', title: 'Blockchain Log', desc: 'On-chain record' },
                { num: '6', title: 'Patient Audit', desc: 'View history' }
              ].map((step, idx) => (
                <div key={idx} className="p-4 border border-purple-200 rounded-lg bg-white text-center hover:shadow-md transition-colors">
                  <div className="text-2xl font-bold text-purple-600 mb-2">{step.num}</div>
                  <p className="font-semibold text-gray-900 text-sm">{step.title}</p>
                  <p className="text-xs text-gray-600 mt-1">{step.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Architecture */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">System Architecture</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Application Layer</h3>
                <p className="text-sm text-gray-700">Web dashboards for doctors, patients, and admins. Interactive UI with real-time visualization.</p>
              </div>
              <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Blockchain Layer</h3>
                <p className="text-sm text-gray-700">Solidity smart contracts for authentication, immutable logs, and cryptographic key generation & verification.</p>
              </div>
              <div className="p-6 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Backend Layer</h3>
                <p className="text-sm text-gray-700">Python APIs, Web3.py integration, secure data storage, and role-based access control logic.</p>
              </div>
            </div>
          </div>

          {/* Emergency Access */}
          <div className="mb-20 p-6 border border-orange-300 rounded-lg bg-orange-50">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">🚨 Emergency Access Feature</h2>
            <p className="text-gray-800 mb-4">
              Emergency responders request temporary access. Smart contracts generate time-limited cryptographic keys (e.g., 24 hours) that automatically expire. All emergency access is logged on-chain for complete audit trails.
            </p>
            <div className="grid md:grid-cols-4 gap-4">
              {[
                '⚡ Immediate life-saving access',
                '🔐 No permanent access granted',
                '↩️ Automatic security restoration',
                '📋 Complete audit maintenance'
              ].map((benefit, idx) => (
                <div key={idx} className="p-3 bg-white rounded border border-orange-300 text-sm text-gray-800 font-medium">
                  {benefit}
                </div>
              ))}
            </div>
          </div>

          {/* Benefits */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Who Benefits?</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="p-6 border border-purple-200 rounded-lg bg-purple-50">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">👤 Patients</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>✓ Complete data transparency</li>
                  <li>✓ Full control over records</li>
                  <li>✓ Immutable audit trails</li>
                  <li>✓ Peace of mind & privacy</li>
                </ul>
              </div>
              <div className="p-6 border border-purple-200 rounded-lg bg-purple-50">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🏥 Providers</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>✓ Streamlined secure access</li>
                  <li>✓ Emergency protocols built-in</li>
                  <li>✓ Reduced liability risks</li>
                  <li>✓ Regulatory compliance</li>
                </ul>
              </div>
              <div className="p-6 border border-purple-200 rounded-lg bg-purple-50">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🏛️ Systems</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>✓ Enhanced data security</li>
                  <li>✓ Reduced data breaches</li>
                  <li>✓ Improved satisfaction</li>
                  <li>✓ Healthcare IT innovation</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Tech Stack */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Tech Stack</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-6 border border-gray-200 rounded-lg bg-white hover:shadow-md transition-colors">
                <h3 className="font-semibold text-gray-900 mb-3">🔧 Development</h3>
                <p className="text-sm text-gray-700">Python 3.x • Next.js • Streamlit • Real-time visualization • Interactive UI</p>
              </div>
              <div className="p-6 border border-gray-200 rounded-lg bg-white hover:shadow-md transition-colors">
                <h3 className="font-semibold text-gray-900 mb-3">⛓️ Blockchain</h3>
                <p className="text-sm text-gray-700">Ethereum Network • Solidity Smart Contracts • Web3.py • Cryptographic Keys</p>
              </div>
            </div>
            <div className="mt-6 p-6 border border-purple-200 rounded-lg bg-purple-50">
              <h3 className="font-semibold text-gray-900 mb-3">🚀 Future Enhancements</h3>
              <ul className="grid md:grid-cols-3 gap-4 text-sm text-gray-700">
                <li>• IoT wearables integration</li>
                <li>• Blockchain prescription tracking</li>
                <li>• Aadhaar biometric auth</li>
              </ul>
            </div>
          </div>

          {/* Timeline */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Development Timeline</h2>
            <div className="space-y-3">
              {[
                { phase: '1', title: 'Foundation', desc: 'Problem analysis & architecture' },
                { phase: '2', title: 'Technology', desc: 'Core tech stack training' },
                { phase: '3', title: 'Architecture', desc: 'System design & component interaction' },
                { phase: '4', title: 'Smart Contracts', desc: 'Blockchain logic implementation' },
                { phase: '5', title: 'Frontend', desc: 'Interactive UI development' },
                { phase: '6', title: 'Emergency Access', desc: 'Break-glass feature rollout' },
                { phase: '7', title: 'Backend Integration', desc: 'Full system deployment' }
              ].map((item, idx) => (
            <div className="flex items-start gap-4 p-4 border border-purple-200 rounded-lg bg-white hover:shadow-md transition-colors">
                  <div className="min-w-8 h-8 bg-gradient-to-br from-purple-600 to-violet-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {item.phase}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{item.title}</h4>
                    <p className="text-sm text-gray-700">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Literature Review */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Literature Review</h2>
            <div className="grid md:grid-cols-2 gap-3">
              {[
                'Ekblaw et al. (2016) - MedRec: Blockchain medical data management',
                'Azaria et al. (2016) - Decentralized access control',
                'Peterson et al. (2016) - Blockchain in health information exchange',
                'HIPAA Security Rule - Patient data protection standards',
                'Fernandez-Aleman et al. (2013) - EHR security & privacy',
                'Kruse et al. (2017) - Healthcare data breach prevention',
                'Zhang & Liu (2010) - Role-based access control',
                'Hu et al. (2014) - Attribute-based access control',
                'Xiao et al. (2013) - Emergency access protocols'
              ].map((ref, idx) => (
                <div key={idx} className="p-3 text-sm text-gray-700 border border-purple-200 rounded bg-white">
                  {ref}
                </div>
              ))}
            </div>
            <div className="mt-6 p-4 bg-yellow-50 border border-yellow-300 rounded-lg text-sm text-yellow-900 font-medium">
              <strong>Key Gap:</strong> Existing solutions lack emergency access protocols with automatic expiration and comprehensive tamper-proof audit trails.
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-purple-200 bg-purple-100 py-12">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <p className="text-lg font-semibold text-gray-900 mb-2">THANK YOU</p>
            <p className="text-gray-800 mb-1">Jayesh Dhoot • Arnav Anand • Neel Butala</p>
            <p className="text-sm text-gray-700">2427030072 • 2427030154 • 2427030157</p>
            <p className="text-xs text-gray-600 mt-4">SecureMedi {new Date().getFullYear()}</p>
          </div>
        </footer>
      </main>
    </>
  );
}
