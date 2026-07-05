import { Download, Filter, Plus, Search } from "lucide-react";
import { OpportunityTable } from "@/components/OpportunityTable";
import { fetchOpportunities } from "@/lib/api";

export default async function DashboardPage() {
  const opportunities = await fetchOpportunities();
  return (
    <>
      <div className="topbar">
        <div>
          <p className="eyebrow">Gratitech workspace</p>
          <h1>Funding pipeline</h1>
        </div>
        <div className="toolbar">
          <button className="button secondary" title="Filter opportunities">
            <Filter size={18} />
            Filter
          </button>
          <button className="button secondary" title="Export current view">
            <Download size={18} />
            Export
          </button>
          <button className="button" title="Add opportunity">
            <Plus size={18} />
            Add
          </button>
        </div>
      </div>

      <section className="grid cols-4">
        <div className="card metric">
          <span className="muted">Top fit</span>
          <strong>86</strong>
          <span className="pill high">Apply</span>
        </div>
        <div className="card metric">
          <span className="muted">Closing soon</span>
          <strong>2</strong>
          <span className="pill medium">45 days</span>
        </div>
        <div className="card metric">
          <span className="muted">Active proposals</span>
          <strong>1</strong>
          <span className="pill">Drafting</span>
        </div>
        <div className="card metric">
          <span className="muted">Trial</span>
          <strong>14d</strong>
          <span className="pill high">Active</span>
        </div>
      </section>

      <div className="section-head" style={{ marginTop: 28 }}>
        <h2>Opportunity search</h2>
        <div className="toolbar">
          <div className="input toolbar">
            <Search size={16} />
            <span className="muted">Keyword, agency, eligibility</span>
          </div>
          <select className="select" aria-label="Source">
            <option>All sources</option>
            <option>Grants.gov</option>
            <option>Manual</option>
          </select>
        </div>
      </div>
      <OpportunityTable opportunities={opportunities} />
    </>
  );
}

