import { redirect } from "next/navigation";

export default function Home() {
  // Check for auth token in localStorage (client-side check)
  // This is a server component, but auth is stored in localStorage
  // The actual redirect happens in the client-side auth provider
  redirect("/login");
}
