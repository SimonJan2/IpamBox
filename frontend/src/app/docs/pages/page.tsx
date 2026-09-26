import { redirect } from "next/navigation";

// /docs/pages has no index of its own — the Pages section lives on /docs.
export default function PagesIndex() {
  redirect("/docs");
}
