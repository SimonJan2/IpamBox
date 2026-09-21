import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Markdown renderer for docs articles — maps elements to the app's Tailwind
 * tokens instead of pulling in @tailwindcss/typography. Internal links ("/…")
 * go through next/link; anything else opens in a new tab.
 */
export function DocsContent({ markdown }: { markdown: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="mb-4 text-2xl font-semibold tracking-tight">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="mb-3 mt-8 border-b pb-1.5 text-lg font-semibold tracking-tight">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="mb-2 mt-6 text-base font-semibold">{children}</h3>
        ),
        h4: ({ children }) => (
          <h4 className="mb-2 mt-4 text-sm font-semibold">{children}</h4>
        ),
        p: ({ children }) => (
          <p dir="auto" className="mb-3 text-sm leading-7">
            {children}
          </p>
        ),
        ul: ({ children }) => (
          <ul className="mb-3 ml-5 list-disc space-y-1 text-sm leading-6 marker:text-muted-foreground">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="mb-3 ml-5 list-decimal space-y-1 text-sm leading-6 marker:text-muted-foreground">
            {children}
          </ol>
        ),
        li: ({ children }) => (
          <li dir="auto" className="pl-1">
            {children}
          </li>
        ),
        a: ({ href, children }) =>
          href?.startsWith("/") ? (
            <Link
              href={href}
              className="font-medium text-emerald-400 underline underline-offset-2 hover:text-emerald-300"
            >
              {children}
            </Link>
          ) : (
            <a
              href={href}
              target="_blank"
              rel="noreferrer"
              className="font-medium text-emerald-400 underline underline-offset-2 hover:text-emerald-300"
            >
              {children}
            </a>
          ),
        strong: ({ children }) => (
          <strong className="font-semibold text-foreground">{children}</strong>
        ),
        blockquote: ({ children }) => (
          <blockquote className="mb-3 border-l-2 border-emerald-500/40 pl-3 text-sm text-muted-foreground">
            {children}
          </blockquote>
        ),
        hr: () => <hr className="my-6 border-border" />,
        code: ({ children }) => (
          <code className="rounded border bg-muted px-1.5 py-0.5 font-mono text-[12px]">
            {children}
          </code>
        ),
        pre: ({ children }) => (
          <pre className="mb-3 overflow-x-auto rounded-md border bg-muted/50 p-3 text-[12px] leading-5 [&_code]:border-0 [&_code]:bg-transparent [&_code]:p-0">
            {children}
          </pre>
        ),
        table: ({ children }) => (
          <div className="mb-4 overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">{children}</table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-muted/50">{children}</thead>
        ),
        th: ({ children }) => (
          <th className="border-b px-3 py-2 text-left font-medium">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td dir="auto" className="border-b px-3 py-2 align-top">
            {children}
          </td>
        ),
      }}
    >
      {markdown}
    </ReactMarkdown>
  );
}
