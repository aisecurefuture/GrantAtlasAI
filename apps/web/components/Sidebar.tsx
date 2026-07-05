import Link from "next/link";
import type { Route } from "next";
import { BookOpen, BriefcaseBusiness, Building2, Gauge, Handshake, Library, ShieldCheck, Target, Trophy, type LucideIcon } from "lucide-react";
import { BrandLogo } from "./BrandLogo";

const nav: Array<{ href: Route; label: string; icon: LucideIcon }> = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/opportunities/seed-tech-001", label: "Opportunities", icon: Target },
  { href: "/contracts", label: "Contracts", icon: BriefcaseBusiness },
  { href: "/proposals/seed-tech-001", label: "Proposals", icon: BookOpen },
  { href: "/library", label: "Library", icon: Library },
  { href: "/past-performance", label: "Past Performance", icon: Trophy },
  { href: "/partners", label: "Partners", icon: Handshake },
  { href: "/organization", label: "Organization", icon: Building2 },
  { href: "/admin", label: "Admin", icon: ShieldCheck }
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <BrandLogo href="/dashboard" tone="light" className="brand" />
      <nav className="nav" aria-label="Main navigation">
        {nav.map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}>
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
