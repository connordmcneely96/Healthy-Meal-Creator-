import Link from "next/link";

import { Button } from "@/components/ui/button";
import { clientEnv } from "@/lib/env";

export function SiteHeader() {
  return (
    <header className="mx-auto flex w-full max-w-4xl flex-col gap-4 py-10 text-center">
      <h1 className="text-4xl font-semibold sm:text-5xl">
        {clientEnv.NEXT_PUBLIC_APP_NAME}
      </h1>
      <p className="text-balance text-base text-muted-foreground sm:text-lg">
        A production-ready monorepo starter. Next.js powers the web UI, Streamlit
        delivers local tooling, and Codespaces makes it easy to collaborate.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Button asChild>
          <Link href="/api/health">Check API health</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="http://localhost:8501" target="_blank">
            Open Streamlit tool
          </Link>
        </Button>
        <Button asChild variant="ghost">
          <Link
            href="https://vercel.com/docs/deployments/overview"
            target="_blank"
            rel="noreferrer"
          >
            Learn about Vercel deployments
          </Link>
        </Button>
      </div>
    </header>
  );
}
