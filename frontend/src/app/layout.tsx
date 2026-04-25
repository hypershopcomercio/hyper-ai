import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Hyper Sync",
    description: "Mercado Livre Integration Dashboard",
};

import { Toaster } from "sonner";
import { AppLayout } from "@/components/AppLayout";

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="pt-BR">
            <body className={inter.className}>
                <AppLayout>
                    {children}
                </AppLayout>
                <Toaster richColors position="top-right" />
            </body>
        </html>
    );
}
