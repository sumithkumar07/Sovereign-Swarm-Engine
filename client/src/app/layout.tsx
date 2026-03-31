import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sovereign | 3.2M Param Titan Swarm",
  description: "Experience the first autonomous local neural swarm with a 100% private 3.2M parameter engine.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased font-sans selection:bg-blue-500/10">
        {children}
      </body>
    </html>
  );
}
