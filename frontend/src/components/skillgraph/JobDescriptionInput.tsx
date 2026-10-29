"use client";

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  hasAnalysis: boolean;
  error: string | null;
}

const MAX_CHARS = 10_000;
const MIN_CHARS = 20;

export function JobDescriptionInput({
  value,
  onChange,
  onSubmit,
  isLoading,
  hasAnalysis,
  error,
}: JobDescriptionInputProps) {
  const charCount = value.length;
  const isTooShort = charCount > 0 && charCount < MIN_CHARS;
  const isTooLong = charCount > MAX_CHARS;
  const isDisabled = isLoading || isTooShort || isTooLong || charCount === 0;

  return (
    <div className="space-y-3">
      {/* Textarea */}
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={isLoading}
          rows={8}
          placeholder={
            "Paste a job description here…\n\nExample:\nRequirements:\n- Python and numpy for data science\n- pytorch or tensorflow for deep learning\n\nNice to have:\n- Docker and kubernetes"
          }
          className="w-full resize-none rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm text-zinc-900 placeholder-zinc-400 shadow-sm transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:placeholder-zinc-500 dark:focus:border-emerald-500 dark:focus:ring-emerald-500/20"
        />
        {/* Character counter */}
        <span
          className={`absolute bottom-2 right-3 text-xs tabular-nums ${
            isTooLong
              ? "text-red-500"
              : charCount > MAX_CHARS * 0.9
              ? "text-amber-500"
              : "text-zinc-400 dark:text-zinc-500"
          }`}
        >
          {charCount.toLocaleString()} / {MAX_CHARS.toLocaleString()}
        </span>
      </div>

      {/* Inline validation messages */}
      {isTooShort && (
        <p className="text-xs text-red-600 dark:text-red-400">
          Job description must be at least {MIN_CHARS} characters.
        </p>
      )}
      {isTooLong && (
        <p className="text-xs text-red-600 dark:text-red-400">
          Job description exceeds the {MAX_CHARS.toLocaleString()}-character limit.
        </p>
      )}

      {/* No-analysis hint */}
      {!hasAnalysis && (
        <p className="text-xs text-zinc-400 dark:text-zinc-500">
          <span className="mr-1">ℹ️</span>
          No repository has been scanned yet. Scan one with RepoMind above to
          get code evidence. You can still analyze the job description alone.
        </p>
      )}

      {/* API error banner */}
      {error && (
        <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 dark:border-red-900/40 dark:bg-red-950/30">
          <span className="mt-0.5 shrink-0 text-red-500">✗</span>
          <p className="text-xs leading-relaxed text-red-700 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Submit button */}
      <button
        onClick={onSubmit}
        disabled={isDisabled}
        className="flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-emerald-700 dark:hover:bg-emerald-600"
      >
        {isLoading ? (
          <>
            <svg
              className="h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8H4z"
              />
            </svg>
            Analyzing…
          </>
        ) : (
          <>
            <span>🔍</span>
            Analyze Skills
          </>
        )}
      </button>
    </div>
  );
}

