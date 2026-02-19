import React from "react";
import { GitHubIcon } from "./GitHubIcon";
import { Lock, CheckCircle2 } from "lucide-react";
import { Repo } from "../../app/dashboard/types";
import { getLangColor, timeAgo } from "../../app/dashboard/utils";

export function RepoCard({
  repo,
  onSelect,
  isSelected,
  disabled,
}: {
  repo: Repo;
  onSelect: () => void;
  isSelected: boolean;
  disabled: boolean;
}) {
  const initials = repo.name.slice(0, 2).toUpperCase();

  return (
    <button
      onClick={onSelect}
      disabled={disabled}
      className={`group relative w-full rounded-lg border p-4 text-left transition-all duration-150 ${
        isSelected
          ? "border-primary bg-primary/4 ring-1 ring-primary/30"
          : "border-border bg-card hover:border-primary/30 hover:bg-accent/30"
      } ${disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer"}`}
    >
      <div className="mb-3 flex items-start justify-between gap-2">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border bg-secondary text-xs font-bold text-foreground">
            {initials}
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold leading-tight text-foreground">{repo.name}</p>
            {repo.description ? (
              <p className="mt-0.5 truncate text-xs text-muted-foreground">{repo.description}</p>
            ) : (
              <p className="mt-0.5 text-xs text-muted-foreground/50 italic">No description</p>
            )}
          </div>
        </div>
        <div className="flex shrink-0 items-center">
          {isSelected ? (
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary">
              <CheckCircle2 className="h-3.5 w-3.5 text-primary-foreground" />
            </div>
          ) : (
            <div className="flex h-6 w-6 items-center justify-center rounded-full border border-border" />
          )}
        </div>
      </div>

      <div className="mb-3">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary/60 px-2 py-0.5 text-xs text-muted-foreground">
          <GitHubIcon className="h-3 w-3" />
          {repo.full_name}
        </span>
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          {repo.private && (
            <>
              <span className="flex items-center gap-1"><Lock className="h-3 w-3" />Private</span>
              <span>·</span>
            </>
          )}
          <span>{timeAgo(repo.updated_at)}</span>
        </div>
        {repo.language && (
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: getLangColor(repo.language) }} />
            {repo.language}
          </span>
        )}
      </div>
    </button>
  );
}

export function RepoCardSkeleton() {
  return (
    <div className="rounded-lg border border-border bg-card p-4 animate-pulse">
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-zinc-200 dark:bg-zinc-700" />
          <div className="space-y-1.5">
            <div className="h-4 w-28 rounded bg-zinc-200 dark:bg-zinc-700" />
            <div className="h-3 w-40 rounded bg-zinc-200 dark:bg-zinc-700" />
          </div>
        </div>
        <div className="h-6 w-6 rounded-full bg-zinc-200 dark:bg-zinc-700" />
      </div>
      <div className="mb-3 h-5 w-32 rounded-full bg-zinc-200 dark:bg-zinc-700" />
      <div className="flex justify-between">
        <div className="h-3 w-16 rounded bg-zinc-200 dark:bg-zinc-700" />
        <div className="h-3 w-14 rounded bg-zinc-200 dark:bg-zinc-700" />
      </div>
    </div>
  );
}
