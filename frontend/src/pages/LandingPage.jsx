import { Link } from 'react-router-dom'
import { ArrowRight, Star, Check, Sparkles, PenTool, TrendingUp, Calendar, Cpu, Workflow, ShieldHalf, Zap, BarChart3, Globe, Command } from 'lucide-react'

const navItems = [
  { label: 'Platform', href: '#platform' },
  { label: 'Workflows', href: '#workflows' },
  { label: 'Insights', href: '#insights' },
  { label: 'Plans', href: '#plans' },
  { label: 'Contact', href: '#contact' },
]

const heroHighlights = [
  {
    title: 'Autonomous browser agents',
    description: 'Launch Chrome, Firefox, and WebKit runs with one command and watch them execute live.',
    icon: Zap,
  },
  {
    title: 'Single source of QA truth',
    description: 'Dashboards, flakiness scores, and evidence streamed into one consistent results hub.',
    icon: BarChart3,
  },
  {
    title: 'Cross-platform coverage',
    description: 'Desktop and mobile device labs ensure every customer journey stays verified.',
    icon: Globe,
  },
  {
    title: 'CI-ready automation',
    description: 'Trigger workflows from CI/CD, gate releases, and sync alerts to Slack or email.',
    icon: Command,
  },
]

const services = [
  {
    title: 'Autonomous Browser Testing',
    description: 'Ship faster with agents that open browsers, execute scripts, capture evidence, and self-heal flaky selectors.',
    highlights: ['Live run playback & screenshots', 'Self-healing locators', 'Parallel desktop & mobile coverage'],
    icon: Cpu,
  },
  {
    title: 'Intelligent Workflows',
    description: 'Model end-to-end QA journeys via natural language. Reuse steps, assert states, and orchestrate data setup.',
    highlights: ['Reusable QA blueprints', 'Visual flow builder', 'Secure secrets & environments'],
    icon: Workflow,
  },
  {
    title: 'Insightful Analytics',
    description: 'Understand quality trends with failure clustering, flakiness scoring, and coverage reporting out of the box.',
    highlights: ['Flakiness scoring', 'Failure root-cause notes', 'Team-ready dashboards'],
    icon: ShieldHalf,
  },
]

const posts = [
  {
    title: 'How autonomous QA caught a checkout regression in 3 minutes',
    category: 'Case Study',
    image: 'bg-[radial-gradient(circle_at_top,#cd8cff,#6d28d9)]',
  },
  {
    title: 'Designing repeatable browser workflows with QA Agent',
    category: 'Guides',
    image: 'bg-[radial-gradient(circle_at_top,#38bdf8,#1e40af)]',
  },
  {
    title: 'Telemetry signals every QA dashboard needs to track',
    category: 'Insights',
    image: 'bg-[radial-gradient(circle_at_top,#f472b6,#db2777)]',
  },
]

const plans = [
  {
    tier: 'Starter',
    tagline: 'Automate the basics in hours',
    price: '$199',
    features: ['5 concurrent browser agents', 'Unlimited quick tests', 'Slack + email notifications', '7-day history'],
  },
  {
    tier: 'Growth',
    tagline: 'Scale coverage with your team',
    price: '$499',
    featured: true,
    features: ['20 concurrent agents', 'Workspace workflows & approvals', 'Insights dashboard exports', '30-day evidence retention'],
  },
  {
    tier: 'Enterprise',
    tagline: 'Compliance, SSO, and custom labs',
    price: 'Let’s talk',
    features: ['Private device clouds', 'SOC2-compliant storage', 'Dedicated success engineer', 'Custom retention policies'],
  },
]

function GlowBackdrop() {
  return (
    <div className="absolute inset-0">
      <div className="absolute -top-32 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-gradient-to-br from-[#8b5cf6]/65 via-[#c084fc]/45 to-transparent blur-[140px] opacity-80" />
      <div className="absolute -bottom-40 left-1/3 h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-gradient-to-tr from-[#6366f1]/45 via-transparent to-transparent blur-[160px] opacity-60" />
      <div className="absolute top-1/2 right-0 h-[360px] w-[360px] -translate-y-1/2 translate-x-1/3 rounded-full bg-gradient-to-tl from-[#f472b6]/45 via-transparent to-transparent blur-[160px] opacity-55" />
    </div>
  )
}

function HeroSection() {
  return (
    <section id="hero" className="relative z-10 overflow-hidden rounded-[32px] bg-black/85 px-6 pb-16 pt-0 sm:px-12 sm:pt-0 lg:px-16 lg:pb-20">
      <GlowBackdrop />
      <header className="relative z-20 mb-16 flex items-center justify-between gap-6 rounded-full border border-white/5 bg-white/5 px-6 py-4 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-tr from-purple-600 to-blue-500">
            <Sparkles className="h-5 w-5" />
          </div>
          <div className="text-sm text-white/70">
            <p className="font-semibold text-white">QA Agent platform</p>
            <p className="text-xs text-white/60">Ship automated QA that keeps up with product velocity.</p>
          </div>
        </div>
        <a
          href="#contact"
          className="rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-purple-500/50 transition hover:shadow-xl hover:shadow-purple-500/60"
        >
          Talk with our team
        </a>
      </header>

      <div className="relative z-20 grid gap-12 lg:grid-cols-2 lg:items-center">
        <div className="space-y-8">
          <div className="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-white/70">
            <div className="flex items-center gap-1 text-emerald-400">
              <Star className="h-4 w-4" />
              <span className="text-xs font-semibold uppercase tracking-wide">Trusted by QA teams shipping daily</span>
            </div>
            <span className="text-white/60">15k+ automated journeys executed</span>
          </div>

          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Helping you launch and <span className="font-serif italic text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-300">scale</span> automated QA
          </h1>

          <p className="max-w-xl text-lg text-white/70">
            QA Agent turns complex end-to-end testing into a guided experience. Build natural-language workflows, stream live evidence, and keep release velocity high without sacrificing coverage.
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <Link
              to="/browser-use"
              className="group inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 px-6 py-3 font-semibold text-white shadow-lg shadow-purple-500/40 transition hover:translate-y-[-1px] hover:shadow-purple-500/60"
            >
              Explore browser agent
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              to="/results"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 px-6 py-3 text-sm font-semibold text-white/80 transition hover:border-white/20 hover:text-white"
            >
              View analytics
            </Link>
            <Link
              to="/settings"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 px-6 py-3 text-sm font-semibold text-white/80 transition hover:border-white/20 hover:text-white"
            >
              Open settings
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {heroHighlights.map((highlight) => (
            <div
              key={highlight.title}
              className="group flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg shadow-purple-900/20 transition-transform hover:-translate-y-1 hover:border-purple-400/50"
            >
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/10 text-purple-200">
                <highlight.icon className="h-5 w-5" />
              </div>
              <h3 className="text-base font-semibold text-white">{highlight.title}</h3>
              <p className="text-sm text-white/70">{highlight.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function ServicesSection() {
  return (
    <section id="platform" className="relative overflow-hidden rounded-[32px] bg-black/85 p-8 sm:p-12 lg:p-16 shadow-[0_25px_80px_rgba(118,75,216,0.25)]">
      <GlowBackdrop />
      <div className="relative z-10 mb-12 text-center">
        <span className="mx-auto inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-white/60">Platform</span>
        <h2 className="mt-6 text-4xl font-semibold text-white sm:text-5xl">
          Everything your QA team needs in one control center
        </h2>
        <p className="mt-4 text-base text-white/60 md:text-lg">
          Orchestrate browsers, data, and reporting with a few clicks—QA Agent handles the heavy lifting automatically.
        </p>
      </div>

      <div className="relative z-10 grid gap-6 md:grid-cols-3">
        {services.map((service) => (
          <div key={service.title} className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-8 transition-transform hover:-translate-y-1 hover:border-purple-400/50">
            <div className="absolute inset-0 bg-gradient-to-br from-white/0 via-white/5 to-white/0 opacity-0 transition-opacity group-hover:opacity-100" />
            <div className="relative z-10 space-y-5">
              <div className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/10">
                <service.icon className="h-5 w-5 text-purple-300" />
              </div>
              <h3 className="text-xl font-semibold text-white">{service.title}</h3>
              <p className="text-sm leading-relaxed text-white/60">{service.description}</p>
              <ul className="mt-6 space-y-3 text-sm text-white/70">
                {service.highlights.map((highlight) => (
                  <li key={highlight} className="flex items-center gap-3">
                    <Check className="h-4 w-4 text-purple-400" />
                    {highlight}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

function AboutSection() {
  return (
    <section id="workflows" className="relative overflow-hidden rounded-[32px] bg-black/85 p-8 sm:p-12 lg:p-16 shadow-[0_25px_80px_rgba(118,75,216,0.25)]">
      <GlowBackdrop />
      <div className="relative z-10 grid gap-10 lg:grid-cols-2 lg:items-center">
        <div>
          <span className="inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-white/60">Workflows</span>
          <h2 className="mt-6 text-4xl font-semibold text-white sm:text-5xl">
            We’re focused on <span className="font-serif italic text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-300">scaling</span> your QA coverage without slowing devs
          </h2>
          <p className="mt-6 text-base leading-relaxed text-white/65">
            Define journeys in natural language, plug in data or assertions, and watch QA Agent translate plans into reliable automation. Teams keep context thanks to live session replays, unified logs, and synced notifications.
          </p>
          <div className="mt-8 grid gap-4 text-sm text-white/70 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <div className="mb-3 flex items-center gap-3 text-white">
                <TrendingUp className="h-5 w-5 text-purple-300" />
                Release Velocity
              </div>
              <p className="text-sm leading-relaxed text-white/65">Ship 3× more deployments per week by automating regression suites and focusing on critical edge cases.</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <div className="mb-3 flex items-center gap-3 text-white">
                <PenTool className="h-5 w-5 text-purple-300" />
                Human-readable scripts
              </div>
              <p className="text-sm leading-relaxed text-white/65">Share workflows with stakeholders using clear narratives while QA Agent handles selectors and assertions underneath.</p>
            </div>
          </div>
        </div>
        <div className="relative">
          <div className="absolute -left-6 -top-6 h-16 w-16 rounded-full bg-purple-500/40 blur-2xl" />
          <div className="absolute -right-8 -bottom-8 h-32 w-32 rounded-full bg-indigo-500/40 blur-3xl" />
          <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-white/10 p-6">
            <div className="h-80 rounded-2xl bg-[url('https://images.unsplash.com/photo-1525182008055-f88b95ff7980?auto=format&fit=crop&w=1000&q=80')] bg-cover bg-center" />
          </div>
        </div>
      </div>
    </section>
  )
}

function BlogSection() {
  return (
    <section id="insights" className="relative overflow-hidden rounded-[32px] bg-black/85 p-8 sm:p-12 lg:p-16 shadow-[0_25px_80px_rgba(118,75,216,0.25)]">
      <GlowBackdrop />
      <div className="relative z-10 text-center">
        <span className="inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-white/60">Insights</span>
        <h2 className="mt-6 text-4xl font-semibold text-white sm:text-5xl">The QA Agent daily digest</h2>
        <p className="mt-4 text-base text-white/60 md:text-lg">Lessons, tactics, and frameworks from teams building resilient shipping pipelines.</p>
      </div>

      <div className="relative z-10 mt-12 grid gap-6 md:grid-cols-3">
        {posts.map((post) => (
          <article key={post.title} className="group flex h-full flex-col overflow-hidden rounded-3xl border border-white/10 bg-white/5">
            <div className={`relative aspect-[4/3] w-full ${post.image} transition-transform duration-300 group-hover:scale-[1.02]`}>
              <div className="absolute inset-0 bg-black/10" />
            </div>
            <div className="flex flex-1 flex-col px-6 pb-6 pt-5">
              <span className="text-xs font-semibold uppercase tracking-wider text-white/60">{post.category}</span>
              <h3 className="mt-3 text-lg font-semibold text-white">{post.title}</h3>
              <button className="mt-auto inline-flex items-center gap-2 text-sm font-medium text-purple-300 transition hover:text-white">
                Read article
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

function PricingSection() {
  return (
    <section id="plans" className="relative overflow-hidden rounded-[32px] bg-black/85 p-8 sm:p-12 lg:p-16 shadow-[0_25px_80px_rgba(118,75,216,0.25)]">
      <GlowBackdrop />
      <div className="relative z-10 text-center">
        <div className="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/70">
          <Star className="h-4 w-4 text-amber-400" />
          <span>Join 230 product teams shipping with confidence</span>
          <div className="flex items-center text-amber-400">
            {[...Array(5)].map((_, idx) => (
              <Star key={idx} className="h-4 w-4 fill-current" />
            ))}
          </div>
        </div>
        <h2 className="mt-6 text-4xl font-semibold text-white sm:text-5xl">
          Simple plans to grow your <span className="font-serif italic text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-300">quality</span>
        </h2>
        <p className="mt-4 text-base text-white/60 md:text-lg">Choose predictable automation that fits your team today—and expands when you need it.</p>
      </div>

      <div className="relative z-10 mt-12 grid gap-6 md:grid-cols-3">
        {plans.map((plan) => (
          <div
            key={plan.tier}
            className={`flex flex-col rounded-3xl border border-white/10 bg-white/5 p-8 shadow-[0_20px_60px_rgba(0,0,0,0.25)] transition-transform hover:-translate-y-1 ${plan.featured ? 'border-purple-500/60 bg-gradient-to-br from-purple-500/20 via-purple-500/5 to-transparent' : ''}`}
          >
            <span className="text-sm font-semibold uppercase tracking-wider text-white/60">{plan.tier}</span>
            <h3 className="mt-3 text-xl font-semibold text-white">{plan.tagline}</h3>
            <p className="mt-6 text-4xl font-semibold text-white">{plan.price}<span className="text-base font-medium text-white/50"> {plan.price === 'Let’s talk' ? '' : '/mo'}</span></p>
            <ul className="mt-6 space-y-3 text-sm text-white/70">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-center gap-3">
                  <Check className="h-4 w-4 text-purple-400" />
                  {feature}
                </li>
              ))}
            </ul>
            <Link
              to={plan.price === 'Let’s talk' ? '/settings' : '/quick-test'}
              className={`mt-8 inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition ${plan.featured ? 'bg-white text-purple-600 hover:bg-purple-50' : 'border border-white/10 text-white/80 hover:text-white hover:border-white/20'}`}
            >
              {plan.price === 'Let’s talk' ? 'Contact sales' : 'Start automating'}
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        ))}
      </div>
    </section>
  )
}

function ContactSection() {
  return (
    <section id="contact" className="relative overflow-hidden rounded-[32px] bg-black/85 p-8 sm:p-12 lg:p-16 shadow-[0_25px_80px_rgba(118,75,216,0.25)]">
      <GlowBackdrop />
      <div className="relative z-10 grid gap-10 lg:grid-cols-2 lg:items-center">
        <div>
          <span className="inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-white/60">Contact</span>
          <h2 className="mt-6 text-4xl font-semibold text-white sm:text-5xl">Ready to put QA Agent to work?</h2>
          <p className="mt-6 text-base leading-relaxed text-white/70">
            Tell us about your release cadence, tech stack, and target devices. We’ll configure the first workflow for you and share a tailored rollout plan.
          </p>
          <div className="mt-8 flex flex-col gap-4 text-sm text-white/70">
            <div className="flex items-center gap-3">
              <Calendar className="h-4 w-4 text-purple-300" />
              Calendars open for onboarding within 72 hours
            </div>
            <div className="flex items-center gap-3">
              <Sparkles className="h-4 w-4 text-purple-300" />
              Dedicated automation specialist from day one
            </div>
          </div>
        </div>

        <form className="relative rounded-3xl border border-white/10 bg-white/5 p-8 space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-wide text-white/60">Name</label>
              <input type="text" placeholder="Jordan Taylor" className="landing-input" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-wide text-white/60">Work email</label>
              <input type="email" placeholder="team@yourcompany.com" className="landing-input" />
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wide text-white/60">Primary goal</label>
            <input type="text" placeholder="Reduce regression testing time" className="landing-input" />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wide text-white/60">How can we help?</label>
            <textarea rows="4" placeholder="Share the apps, browsers, and release cadence you want to support." className="landing-input resize-none" />
          </div>
          <button type="submit" className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 px-6 py-3 font-semibold text-white shadow-lg shadow-purple-500/40 transition hover:translate-y-[-1px] hover:shadow-purple-500/60">
            Request a rollout plan
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>
      </div>
    </section>
  )
}

export default function Home() {
  return (
    <div className="relative flex w-full flex-col gap-12 py-12 sm:py-16 lg:py-20">
      <HeroSection />
      <ServicesSection />
      <AboutSection />
      <BlogSection />
      <PricingSection />
      <ContactSection />
      <footer className="rounded-[32px] border border-white/5 bg-black/80 p-8 text-center text-xs text-white/50">
        © {new Date().getFullYear()} QA Agent. Automated quality for fearless releases.
      </footer>
    </div>
  )
}
