import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GrantAtlas.ai",
  description: "AI-powered funding intelligence for grants and contracts",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/brand/grantatlas-mark.svg"
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
