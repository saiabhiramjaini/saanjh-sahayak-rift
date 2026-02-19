"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Header } from "@/components/header";
import {
  Zap,
  Bot,
  Shield,
  BarChart3,
  GitBranch,
  CheckCircle2,
  ArrowRight,
  Play,
} from "lucide-react";

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
    </svg>
  );
}

const steps = [
  {
    number: "01",
    title: "Connect Repository",
    description: "Link your GitHub repository with a single click.",
  },
  {
    number: "02",
    title: "Run Tests",
    description: "GreenBranch automatically runs your test suite.",
  },
  {
    number: "03",
    title: "Detect Issues",
    description: "AI analyzes failures and identifies root causes.",
  },
  {
    number: "04",
    title: "Apply Fixes",
    description: "Automated fixes are committed to a new branch.",
  },
  {
    number: "05",
    title: "Verify Success",
    description: "Tests rerun until the pipeline turns green.",
  },
];

const features = [
  {
    icon: Zap,
    title: "Saves Developer Time",
    description:
      "Stop debugging CI failures manually. GreenBranch handles it autonomously.",
  },
  {
    icon: Bot,
    title: "Fully Autonomous",
    description:
      "No human intervention required. The agent works independently.",
  },
  {
    icon: Shield,
    title: "Safe Execution",
    description:
      "All changes happen on a new branch. Your main branch stays protected.",
  },
  {
    icon: BarChart3,
    title: "Transparent Results",
    description:
      "Every action is logged and displayed. Full visibility into all fixes.",
  },
];

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header variant="landing" />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden">
          <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 sm:py-32 lg:px-8">
            <div className="mx-auto max-w-3xl text-center">
              <div className="mb-8 flex justify-center">
                <div className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary px-4 py-1.5 text-sm text-muted-foreground">
                  <GitBranch className="h-4 w-4 text-primary" />
                  Autonomous CI/CD Healing
                </div>
              </div>

              <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl">
                Keep your CI pipelines{" "}
                <span className="text-primary">green</span>
              </h1>

              <p className="mt-6 text-lg leading-8 text-muted-foreground">
                GreenBranch automatically detects, fixes, and verifies code
                issues. Stop wasting time on broken builds.
              </p>

              <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
                <Link href="/signin">
                  <Button size="lg" className="w-full gap-2 sm:w-auto">
                    <GitHubIcon className="h-5 w-5" />
                    Sign in with GitHub
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  size="lg"
                  className="w-full gap-2 sm:w-auto"
                >
                  <Play className="h-4 w-4" />
                  View Demo
                </Button>
              </div>
            </div>
          </div>

          {/* Background gradient */}
          <div className="absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute left-1/2 top-0 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-3xl" />
          </div>
        </section>

        {/* How It Works Section */}
        <section className="border-t border-border bg-secondary/30">
          <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                How it works
              </h2>
              <p className="mt-4 text-muted-foreground">
                Five simple steps to automated CI healing
              </p>
            </div>

            <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-5">
              {steps.map((step, index) => (
                <div key={step.number} className="relative">
                  <div className="flex flex-col items-center text-center">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground font-mono text-sm font-semibold">
                      {step.number}
                    </div>
                    <h3 className="mt-4 text-base font-semibold text-foreground">
                      {step.title}
                    </h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {step.description}
                    </p>
                  </div>
                  {index < steps.length - 1 && (
                    <div className="absolute left-full top-6 hidden w-full -translate-x-1/2 lg:block">
                      <ArrowRight className="mx-auto h-5 w-5 text-border" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="border-t border-border">
          <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Why GreenBranch?
              </h2>
              <p className="mt-4 text-muted-foreground">
                Built for developers who value their time
              </p>
            </div>

            <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {features.map((feature) => (
                <div
                  key={feature.title}
                  className="group rounded-lg border border-border bg-card p-6 transition-colors hover:border-primary/50"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <h3 className="mt-4 text-base font-semibold text-foreground">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Trust Section */}
        <section className="border-t border-border bg-secondary/30">
          <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-3xl">
              <div className="rounded-lg border border-border bg-card p-8">
                <h2 className="text-xl font-semibold text-foreground">
                  Safe by Design
                </h2>
                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                    <div>
                      <p className="font-medium text-foreground">
                        Protected Main Branch
                      </p>
                      <p className="text-sm text-muted-foreground">
                        GreenBranch never edits your main branch directly
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                    <div>
                      <p className="font-medium text-foreground">
                        Isolated Branches
                      </p>
                      <p className="text-sm text-muted-foreground">
                        All changes happen on a new dedicated branch
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                    <div>
                      <p className="font-medium text-foreground">
                        Commit History
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Every fix is committed with clear messages
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                    <div>
                      <p className="font-medium text-foreground">
                        Full Audit Log
                      </p>
                      <p className="text-sm text-muted-foreground">
                        All actions are logged and visible on dashboard
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="border-t border-border">
          <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Ready to go green?
              </h2>
              <p className="mt-4 text-muted-foreground">
                Connect your repository and let GreenBranch handle the rest.
              </p>
              <div className="mt-8">
                <Link href="/signin">
                  <Button size="lg" className="gap-2">
                    <GitHubIcon className="h-5 w-5" />
                    Get Started
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-2">
              <Image
                src="/logo.png"
                alt="GreenBranch"
                width={24}
                height={24}
                className="h-6 w-6"
              />
              <span className="text-sm text-muted-foreground">
                GreenBranch
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Automatically detect, fix, and verify code issues to keep CI
              pipelines green.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
