import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TeamMento AI",
  description: "Hackathon MVP showing experience-to-memory learning loop",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
