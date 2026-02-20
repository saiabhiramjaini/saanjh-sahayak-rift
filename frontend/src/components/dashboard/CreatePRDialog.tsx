"use client";

import { useState, useEffect, useCallback } from "react";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import {
  CheckCircle2,
  GitPullRequest,
  GitBranch,
  GitCommit,
  FileCode,
  Loader2,
  Sparkles,
  AlertCircle,
  Edit3,
  Clock,
  Users,
  UserCircle,
} from "lucide-react";
import { Fix } from "@/app/dashboard/types";
import axios from "axios";

interface CreatePRDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  repoUrl: string;
  branchName: string;
  baseBranch?: string;
  commitHash?: string;
  fixes: Fix[];
  timeTaken?: number;
  teamName?: string;
  teamLeaderName?: string;
  githubToken?: string;
  onPRCreated: (prUrl: string, repoName: string) => void;
}

/** Parse `owner/repo` from a full GitHub URL. */
function parseRepoFullName(url: string): string {
  const clean = url.replace(/\.git$/, "").replace(/\/$/, "");
  const parts = clean.split("/");
  return `${parts[parts.length - 2]}/${parts[parts.length - 1]}`;
}

/** Format seconds as M:SS */
function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

/** Build a rich markdown PR body using all available context. */
function buildPRBody(
  fixes: Fix[],
  repoFullName: string,
  branchName: string,
  baseBranch: string,
  commitHash: string | undefined,
  timeTaken: number | undefined,
  teamName: string | undefined,
  teamLeaderName: string | undefined
): string {
  const fixedFixes = fixes.filter((f) => f.status === "fixed");
  const failedFixes = fixes.filter((f) => f.status === "failed");
  const now = new Date().toISOString();

  let body = `# 🤖 GreenBranch AI — Automated Fix Report\n\n`;

  // ── Summary table ─────────────────────────────────────────────────────
  body += `## Summary\n\n`;
  body += `| Field | Value |\n`;
  body += `| --- | --- |\n`;
  body += `| **Repository** | \`${repoFullName}\` |\n`;
  body += `| **Fix Branch** | \`${branchName}\` |\n`;
  body += `| **Target Branch** | \`${baseBranch}\` |\n`;
  if (commitHash) body += `| **Commit** | \`${commitHash}\` |\n`;
  if (timeTaken) body += `| **Time Taken** | ${formatTime(timeTaken)} |\n`;
  body += `| **Files Fixed** | ${fixedFixes.length} |\n`;
  body += `| **Generated At** | ${now} |\n`;
  if (teamName) body += `| **Team** | ${teamName} |\n`;
  if (teamLeaderName) body += `| **Team Leader** | ${teamLeaderName} |\n`;
  body += `\n---\n\n`;

  // ── Detailed fixes ────────────────────────────────────────────────────
  if (fixedFixes.length > 0) {
    body += `## ✅ Fixes Applied (${fixedFixes.length})\n\n`;
    fixedFixes.forEach((fix, idx) => {
      body += `### ${idx + 1}. \`${fix.file}\`\n\n`;

      if (fix.bug_type) {
        body += `**Bug Type:** \`${fix.bug_type}\``;
        if (fix.line_number) body += ` &nbsp;·&nbsp; **Line:** ${fix.line_number}`;
        body += `\n\n`;
      }

      if (fix.commit_message) {
        body += `**Commit Message:** ${fix.commit_message}\n\n`;
      }

      if (fix.explanation) {
        if (fix.explanation.root_cause) {
          body += `**Root Cause:**\n> ${fix.explanation.root_cause}\n\n`;
        }
        if (fix.explanation.changes_made) {
          body += `**Changes Made:**\n> ${fix.explanation.changes_made}\n\n`;
        }
        if (fix.explanation.impact) {
          body += `**Impact:**\n> ${fix.explanation.impact}\n\n`;
        }
      } else if (fix.description) {
        body += `**Description:** ${fix.description}\n\n`;
      }

      body += `---\n\n`;
    });
  }

  // ── Failed fixes ──────────────────────────────────────────────────────
  if (failedFixes.length > 0) {
    body += `## ⚠️ Attempted But Could Not Fix (${failedFixes.length})\n\n`;
    failedFixes.forEach((fix) => {
      body += `- \`${fix.file}\``;
      if (fix.bug_type) body += ` (${fix.bug_type})`;
      if (fix.error_message) body += ` — ${fix.error_message}`;
      body += `\n`;
    });
    body += `\n---\n\n`;
  }

  // ── Footer ────────────────────────────────────────────────────────────
  body += `> *This Pull Request was automatically generated by [GreenBranch AI](https://greenbranch.d6vs.tech). `;
  body += `All changes have been verified by the automated test suite before this PR was raised.*\n`;

  return body;
}

/** Build a concise, descriptive PR title from the fix set. */
function buildPRTitle(fixes: Fix[], repoFullName: string): string {
  const fixedFixes = fixes.filter((f) => f.status === "fixed");

  if (fixedFixes.length === 0) {
    return `fix: Automated bug fixes for ${repoFullName.split("/")[1]}`;
  }

  if (fixedFixes.length === 1) {
    const fix = fixedFixes[0];
    if (fix.commit_message) {
      // Use commit message but strip any leading "fix:" prefix duplication
      const msg = fix.commit_message.replace(/^fix:\s*/i, "").trim();
      return `fix: ${msg.slice(0, 72)}`;
    }
    return `fix: Resolve ${fix.bug_type || "bug"} in ${fix.file}`;
  }

  // Multiple fixes — use the most common bug type if consistent
  const bugTypes = fixedFixes.map((f) => f.bug_type).filter(Boolean);
  const uniqueTypes = [...new Set(bugTypes)];
  if (uniqueTypes.length === 1 && uniqueTypes[0]) {
    return `fix: Resolve ${fixedFixes.length} ${uniqueTypes[0]} issues in ${repoFullName.split("/")[1]}`;
  }

  return `fix: Apply ${fixedFixes.length} AI-generated bug fixes to ${repoFullName.split("/")[1]}`;
}

// ─────────────────────────────────────────────────────────────────────────────

export function CreatePRDialog({
  open,
  onOpenChange,
  repoUrl,
  branchName,
  baseBranch = "main",
  commitHash,
  fixes,
  timeTaken,
  teamName,
  teamLeaderName,
  githubToken,
  onPRCreated,
}: CreatePRDialogProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [prTitle, setPrTitle] = useState("");
  const [prBody, setPrBody] = useState("");

  const repoFullName = parseRepoFullName(repoUrl);

  /** Recompute title + body whenever the dialog opens or key props change. */
  const recomputeContent = useCallback(() => {
    setPrTitle(buildPRTitle(fixes, repoFullName));
    setPrBody(
      buildPRBody(
        fixes,
        repoFullName,
        branchName,
        baseBranch,
        commitHash,
        timeTaken,
        teamName,
        teamLeaderName
      )
    );
    setError(null);
    setIsEditing(false);
  }, [
    fixes,
    repoFullName,
    branchName,
    baseBranch,
    commitHash,
    timeTaken,
    teamName,
    teamLeaderName,
  ]);

  // Refresh content every time the dialog opens
  useEffect(() => {
    if (open) recomputeContent();
  }, [open, recomputeContent]);

  const fixedFixes = fixes.filter((f) => f.status === "fixed");

  const handleCreatePR = async () => {
    if (!githubToken) {
      setError("GitHub token not available. Please sign in with GitHub.");
      return;
    }
    if (!branchName) {
      setError("No branch name available. The pipeline may not have committed changes yet.");
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      // ✅ Correct: PR endpoint lives on the AI server, NOT the EC2 agent
      const aiServerUrl = process.env.NEXT_PUBLIC_AGENT_SERVER_URL;
      if (!aiServerUrl) {
        throw new Error("NEXT_PUBLIC_AGENT_SERVER_URL is not configured.");
      }

      const response = await axios.post(`${aiServerUrl}/api/v1/pr`, {
        repo_full_name: repoFullName,
        branch_name: branchName,
        base_branch: baseBranch,
        title: prTitle,
        body: prBody,
        github_token: githubToken,
      });

      if (response.data.success) {
        onPRCreated(response.data.pr_url, repoFullName);
        onOpenChange(false);
      } else {
        setError(response.data.message || "Failed to create PR. Please try again.");
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string; message?: string } }; message?: string };
      const message =
        axiosErr.response?.data?.detail ||
        axiosErr.response?.data?.message ||
        axiosErr.message ||
        "Unknown error";
      setError(`Failed to create PR: ${message}`);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="sm:max-w-2xl border-primary/20 bg-card overflow-hidden max-h-[90vh] overflow-y-auto">
        {/* Decorative background blobs */}
        <div className="pointer-events-none absolute -top-20 -left-20 h-40 w-40 rounded-full bg-primary/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 -right-20 h-40 w-40 rounded-full bg-primary/10 blur-3xl" />

        <AlertDialogHeader className="relative">
          {/* Success icon */}
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-primary/20 to-primary/5 ring-1 ring-primary/20">
                <CheckCircle2 className="h-10 w-10 text-primary" />
              </div>
              <div className="absolute -right-1 -bottom-1 flex h-8 w-8 items-center justify-center rounded-full bg-background ring-4 ring-background">
                <GitPullRequest className="h-5 w-5 text-primary" />
              </div>
            </div>
          </div>

          <AlertDialogTitle className="text-2xl text-center">
            All Tests Passed! 🎉
          </AlertDialogTitle>
          <AlertDialogDescription className="text-center text-base">
            GreenBranch fixed your code. Review the details below and raise a Pull Request.
          </AlertDialogDescription>
        </AlertDialogHeader>

        {/* ── Content ──────────────────────────────────────────────────── */}
        <div className="space-y-4 py-4">

          {/* Quick stats */}
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-lg border border-border/50 bg-secondary/20 p-3 text-center">
              <div className="flex justify-center mb-1.5">
                <FileCode className="h-4 w-4 text-primary" />
              </div>
              <p className="text-lg font-bold text-foreground">{fixedFixes.length}</p>
              <p className="text-xs text-muted-foreground">Files Fixed</p>
            </div>
            <div className="rounded-lg border border-border/50 bg-secondary/20 p-3 text-center">
              <div className="flex justify-center mb-1.5">
                <GitCommit className="h-4 w-4 text-purple-500" />
              </div>
              <p className="text-lg font-bold text-foreground">{fixedFixes.length}</p>
              <p className="text-xs text-muted-foreground">Commits</p>
            </div>
            <div className="rounded-lg border border-border/50 bg-secondary/20 p-3 text-center">
              <div className="flex justify-center mb-1.5">
                <Clock className="h-4 w-4 text-blue-500" />
              </div>
              <p className="text-lg font-bold text-foreground">
                {timeTaken ? formatTime(timeTaken) : "--"}
              </p>
              <p className="text-xs text-muted-foreground">Time Taken</p>
            </div>
          </div>

          {/* Branch / commit info */}
          <div className="rounded-xl border border-border/50 bg-secondary/20 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <GitBranch className="h-4 w-4 text-primary" />
                <span>Fix Branch</span>
              </div>
              <code className="text-sm font-mono text-primary">{branchName || "—"}</code>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <GitBranch className="h-4 w-4 text-muted-foreground" />
                <span>Target Branch</span>
              </div>
              <code className="text-sm font-mono text-foreground">{baseBranch}</code>
            </div>
            {commitHash && (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <GitCommit className="h-4 w-4 text-purple-500" />
                  <span>Commit Hash</span>
                </div>
                <code className="text-sm font-mono text-foreground">{commitHash.slice(0, 8)}</code>
              </div>
            )}
          </div>

          {/* Team info */}
          {(teamName || teamLeaderName) && (
            <div className="rounded-xl border border-border/50 bg-secondary/20 p-4 space-y-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Team
              </p>
              <div className="flex gap-4 flex-wrap">
                {teamName && (
                  <div className="flex items-center gap-2 text-sm">
                    <Users className="h-3.5 w-3.5 text-muted-foreground" />
                    <span className="text-muted-foreground">Team:</span>
                    <span className="font-medium text-foreground">{teamName}</span>
                  </div>
                )}
                {teamLeaderName && (
                  <div className="flex items-center gap-2 text-sm">
                    <UserCircle className="h-3.5 w-3.5 text-muted-foreground" />
                    <span className="text-muted-foreground">Leader:</span>
                    <span className="font-medium text-foreground">{teamLeaderName}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* PR title & body editor */}
          <div className="rounded-xl border border-border/50 bg-secondary/20 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Pull Request Details
              </p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditing((v) => !v)}
                className="h-7 gap-1.5 text-xs"
              >
                <Edit3 className="h-3 w-3" />
                {isEditing ? "Done" : "Edit"}
              </Button>
            </div>

            {isEditing ? (
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-foreground">PR Title</label>
                  <Input
                    value={prTitle}
                    onChange={(e) => setPrTitle(e.target.value)}
                    className="bg-background/50 text-sm"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-foreground">PR Description (Markdown)</label>
                  <Textarea
                    value={prBody}
                    onChange={(e) => setPrBody(e.target.value)}
                    className="bg-background/50 text-sm min-h-[200px] font-mono text-xs"
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="rounded-lg bg-background/50 px-3 py-2">
                  <p className="text-xs text-muted-foreground mb-1">Title</p>
                  <p className="text-sm font-medium text-foreground">{prTitle}</p>
                </div>
                <div className="rounded-lg bg-background/50 px-3 py-2 max-h-40 overflow-y-auto">
                  <p className="text-xs text-muted-foreground mb-1">Description Preview</p>
                  <pre className="text-xs text-foreground/80 whitespace-pre-wrap font-mono leading-relaxed">
                    {prBody.slice(0, 500)}{prBody.length > 500 ? "\n…" : ""}
                  </pre>
                </div>
              </div>
            )}
          </div>

          {/* Changes to be included */}
          {fixedFixes.length > 0 && (
            <div className="rounded-xl border border-border/50 bg-secondary/20 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                Changes to be included ({fixedFixes.length})
              </p>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {fixedFixes.map((fix, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 rounded-lg bg-background/50 px-3 py-2"
                  >
                    <CheckCircle2 className="h-4 w-4 text-primary shrink-0" />
                    <code className="text-xs font-mono text-foreground flex-1 truncate">
                      {fix.file}
                    </code>
                    {fix.line_number > 0 && (
                      <span className="text-[10px] text-muted-foreground shrink-0">
                        L{fix.line_number}
                      </span>
                    )}
                    <Badge variant="outline" className="text-[9px] uppercase shrink-0">
                      {fix.bug_type}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Errors / warnings */}
          {!githubToken && (
            <div className="flex items-center gap-2 rounded-lg bg-amber-500/10 border border-amber-500/20 px-3 py-2.5">
              <AlertCircle className="h-4 w-4 text-amber-500 shrink-0" />
              <p className="text-xs text-amber-500">
                Sign in with GitHub to create a Pull Request
              </p>
            </div>
          )}

          {error && (
            <div className="flex items-start gap-2 rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2.5">
              <AlertCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
              <p className="text-xs text-destructive">{error}</p>
            </div>
          )}
        </div>

        <Separator className="opacity-50" />

        <AlertDialogFooter className="flex-col sm:flex-row gap-2 pt-4">
          <AlertDialogCancel disabled={isCreating}>
            Cancel
          </AlertDialogCancel>
          <Button
            onClick={handleCreatePR}
            disabled={isCreating || !githubToken || !branchName}
            className="gap-2"
          >
            {isCreating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating PR…
              </>
            ) : (
              <>
                <GitPullRequest className="h-4 w-4" />
                Create Pull Request
              </>
            )}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
