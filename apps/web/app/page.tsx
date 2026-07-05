import { BrandLogo } from "@/components/BrandLogo";
import {
  ArrowRight,
  BadgeCheck,
  BriefcaseBusiness,
  CalendarClock,
  FileText,
  LockKeyhole,
  Radar,
  Search,
  Sparkles,
  Target,
} from "lucide-react";

export default function Home() {
  const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? "https://app.grantatlas.ai";
  const pipeline = [
    { name: "NSF CyberCorps Scholarship Support", type: "Federal grant", score: 91, action: "Apply" },
    { name: "Community AI Literacy Capacity Fund", type: "Foundation", score: 86, action: "Apply" },
    { name: "Cybersecurity Training Technical Assistance", type: "SAM.gov", score: 84, action: "Pursue" },
  ];

  return (
    <main className="marketing-site">
      <header className="marketing-nav">
        <BrandLogo href="/" className="marketing-brand" />
        <nav aria-label="Marketing navigation">
          <a href="#product">Product</a>
          <a href="#security">Security</a>
          <a href="#pricing">Pricing</a>
          <a href={`${appUrl}/login`}>Sign in</a>
        </nav>
      </header>

      <section className="marketing-hero">
        <div className="hero-copy">
          <span className="hero-kicker">
            <Sparkles size={16} />
            AI-powered funding intelligence
          </span>
          <h1>Find, score, and win more grants and contracts.</h1>
          <p>
            GrantAtlas helps nonprofits, universities, researchers, and growth-stage contractors discover funding, explain fit, manage deadlines, and build proposal workspaces from one secure platform.
          </p>
          <div className="hero-actions">
            <a className="button" href={`${appUrl}/login`}>
              Start 14-day trial
              <ArrowRight size={18} />
            </a>
            <a className="button secondary" href="#product">
              See workflow
            </a>
          </div>
          <div className="proof-row" aria-label="Platform proof points">
            <span><BadgeCheck size={16} /> Grants.gov ready</span>
            <span><BadgeCheck size={16} /> SAM.gov v2 scaffold</span>
            <span><BadgeCheck size={16} /> Tenant isolated</span>
          </div>
        </div>

        <div className="hero-product" aria-label="GrantAtlas product preview">
          <div className="product-topbar">
            <span>Funding pipeline</span>
            <span className="pill high">Live scoring</span>
          </div>
          <div className="product-grid">
            <div className="product-panel wide">
              <div className="panel-header">
                <Radar size={18} />
                Top opportunities
              </div>
              {pipeline.map((item) => (
                <div className="pipeline-row" key={item.name}>
                  <div>
                    <strong>{item.name}</strong>
                    <span>{item.type}</span>
                  </div>
                  <div className="mini-score">{item.score}</div>
                  <span className="pill high">{item.action}</span>
                </div>
              ))}
            </div>
            <div className="product-panel">
              <div className="panel-header">
                <Target size={18} />
                Fit reasons
              </div>
              <p>Mission overlap, eligibility, deadline runway, award size, past performance, partner needs, and strategic value are scored with clear explanations.</p>
            </div>
            <div className="product-panel">
              <div className="panel-header">
                <CalendarClock size={18} />
                Deadlines
              </div>
              <p>Prioritize closing-soon opportunities and route proposal tasks before review windows disappear.</p>
            </div>
          </div>
        </div>
      </section>

      <section id="product" className="marketing-section">
        <div className="section-title">
          <p className="eyebrow">One workflow</p>
          <h2>From discovery to submission-ready workspace</h2>
        </div>
        <div className="feature-grid">
          {[
            ["Discover", Search, "Ingest Grants.gov opportunities first, with SAM.gov contract capture ready for v2 expansion."],
            ["Score", Target, "Rank opportunities against each tenant profile with transparent rules and explainable fit reasons."],
            ["Prepare", FileText, "Create proposal workspaces, compliance matrices, reusable content, budgets, and reviewer tasks."],
            ["Capture", BriefcaseBusiness, "Track NAICS/PSC fit, partners, past performance, bid decisions, and color-team reviews."],
          ].map(([title, Icon, body]) => {
            const TypedIcon = Icon as typeof Search;
            return (
              <article className="feature-card" key={title as string}>
                <TypedIcon size={24} />
                <h3>{title as string}</h3>
                <p>{body as string}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section id="security" className="marketing-band">
        <div>
          <p className="eyebrow">Built for serious funding teams</p>
          <h2>Multi-tenant by design, with security controls from day one.</h2>
        </div>
        <div className="security-list">
          {["Tenant-level data isolation", "Role-based access", "Audit logs", "Environment-based secrets", "Docker Compose deployment", "Caddy automatic TLS"].map((item) => (
            <span key={item}><LockKeyhole size={16} />{item}</span>
          ))}
        </div>
      </section>

      <section id="pricing" className="marketing-section pricing-section">
        <div className="section-title">
          <p className="eyebrow">Simple start</p>
          <h2>Launch with a 14-day trial, then grow by team size and workflow depth.</h2>
        </div>
        <div className="pricing-grid">
          {[
            ["Starter", "Single-organization grant tracking", "$49"],
            ["Professional", "Collaboration, workspaces, and exports", "$149"],
            ["Growth", "Advanced scoring and larger teams", "$399"],
            ["Enterprise", "SSO-ready architecture and API access", "Custom"],
          ].map(([plan, description, price]) => (
            <article className="pricing-card" key={plan}>
              <h3>{plan}</h3>
              <strong>{price}</strong>
              <p>{description}</p>
            </article>
          ))}
        </div>
      </section>

      <footer className="marketing-footer">
        <span>GrantAtlas.ai</span>
        <span>AI-powered funding intelligence for grants and contracts.</span>
      </footer>
    </main>
  );
}
