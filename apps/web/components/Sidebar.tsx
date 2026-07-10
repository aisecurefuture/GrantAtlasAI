"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  BriefcaseBusiness,
  Building2,
  CreditCard,
  Gauge,
  Handshake,
  Library,
  LogOut,
  ShieldCheck,
  Trophy,
  type LucideIcon,
} from "lucide-react";
import { BrandLogo } from "./BrandLogo";
import { logoutAction } from "@/app/actions/auth";

type NavItem = { href: string; label: string; icon: LucideIcon; superAdmin?: boolean };

const nav: NavItem[] = [
  { href: "/dashboard", label: "Pipeline", icon: Gauge },
  { href: "/contracts", label: "Contracts", icon: BriefcaseBusiness },
  { href: "/proposals", label: "Proposals", icon: BookOpen },
  { href: "/library", label: "Content Library", icon: Library },
  { href: "/past-performance", label: "Past Performance", icon: Trophy },
  { href: "/partners", label: "Partners", icon: Handshake },
  { href: "/organization", label: "Organization", icon: Building2 },
  { href: "/billing", label: "Billing", icon: CreditCard },
  { href: "/admin", label: "Admin", icon: ShieldCheck, superAdmin: true },
];

export function Sidebar({
  workspaceName,
  role,
  isSuperAdmin,
}: {
  workspaceName: string;
  role: string;
  isSuperAdmin: boolean;
}) {
  const pathname = usePathname();
  const items = nav.filter((item) => !item.superAdmin || isSuperAdmin);

  return (
    <aside className="sidebar">
      <BrandLogo href="/dashboard" tone="light" className="brand" />
      <nav className="nav" aria-label="Main navigation">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link key={item.href} href={item.href} className={active ? "active" : undefined} aria-current={active ? "page" : undefined}>
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="sidebar-footer">
        <div className="account">
          <span className="account-name">{workspaceName}</span>
          <span className="account-role muted">{role}</span>
        </div>
        <form action={logoutAction}>
          <button className="button ghost" type="submit" title="Sign out">
            <LogOut size={16} />
            Sign out
          </button>
        </form>
      </div>
    </aside>
  );
}
