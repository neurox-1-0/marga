import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

export const metadata: Metadata = {
  title: "Marga | Supply Chain Intelligence",
  description: "Global Supply Chain Agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="text-on-surface font-body-md antialiased overflow-x-hidden">
        <Sidebar />
        <Topbar />
        {children}
      </body>
    </html>
  );
}
