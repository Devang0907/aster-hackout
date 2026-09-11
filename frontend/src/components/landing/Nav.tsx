import { useEffect, useState } from "react";
import { Menu, X, ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Logo } from "./Logo";
import { isAuthenticated, getUser, logout } from "@/lib/auth";
import { get } from "@/lib/api";

const links = [
  { label: "Product", href: "#product" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Solutions", href: "#solutions" },
  { label: "Impact", href: "#impact" },
];

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [factories, setFactories] = useState<any[]>([]);
  const [selectedFactory, setSelectedFactory] = useState<any>(null);
  const [factoryDropdownOpen, setFactoryDropdownOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const authStatus = isAuthenticated();
    setAuthenticated(authStatus);
    if (authStatus) {
      setUser(getUser());
      fetchFactories();
    }
  }, []);

  const fetchFactories = async () => {
    try {
      const response = await get("/api/v1/factories");
      const data = await response.json();
      setFactories(data);
      if (data.length > 0) {
        setSelectedFactory(data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch factories:", error);
    }
  };

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  return (
    <motion.header
      initial={false}
      className="fixed inset-x-0 top-0 z-50"
    >
      <motion.div
        layout
        transition={{ type: "spring", stiffness: 280, damping: 28 }}
        className={`mx-auto flex items-center justify-between transition-all duration-500 ${
          scrolled
            ? "mt-3 max-w-5xl rounded-full border border-border/70 bg-background/70 px-4 py-2 shadow-float backdrop-blur-xl sm:px-6"
            : "max-w-[1400px] bg-transparent px-5 py-4 sm:px-8 lg:px-14"
        }`}
      >
        <a href="#top" className="shrink-0">
          <Logo />
        </a>

        <nav className="hidden flex-1 items-center justify-center gap-8 lg:flex">
          {links.map((l) => (
            <a
              key={l.label}
              href={l.href}
              className="whitespace-nowrap text-[0.6875rem] font-semibold uppercase tracking-[0.18em] text-secondary/80 transition-colors hover:text-primary"
            >
              {l.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center justify-end gap-2.5 lg:flex">
          {authenticated ? (
            <>
              {/* Factory Selector */}
              {factories.length > 0 && (
                <div className="relative">
                  <button
                    onClick={() => setFactoryDropdownOpen(!factoryDropdownOpen)}
                    className="flex items-center gap-2 rounded-full border border-border bg-surface px-4 py-2.5 text-[0.6875rem] font-semibold uppercase tracking-[0.16em] text-primary transition-colors hover:bg-mist"
                  >
                    {selectedFactory?.name || "Select Factory"}
                    <ChevronDown className="h-4 w-4" />
                  </button>
                  {factoryDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-48 rounded-lg border border-border bg-surface shadow-float">
                      {factories.map((factory) => (
                        <button
                          key={factory.id}
                          onClick={() => {
                            setSelectedFactory(factory);
                            setFactoryDropdownOpen(false);
                          }}
                          className="block w-full px-4 py-2 text-left text-sm text-secondary hover:bg-mist hover:text-primary"
                        >
                          {factory.name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
              <a
                href="/dashboard"
                className="rounded-full bg-primary px-5 py-2.5 text-[0.6875rem] font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90"
              >
                Dashboard
              </a>
              <button
                onClick={handleLogout}
                className="rounded-full border border-border bg-surface px-5 py-2.5 text-[0.6875rem] font-semibold uppercase tracking-[0.16em] text-primary transition-colors hover:bg-mist"
              >
                Sign Out
              </button>
            </>
          ) : (
            <>
              <a
                href="/signin"
                className={`rounded-full border px-5 py-2.5 text-[0.6875rem] font-semibold uppercase tracking-[0.16em] transition-colors ${
                  scrolled
                    ? "border-border bg-surface text-primary hover:bg-mist"
                    : "border-border/60 bg-background/50 text-primary hover:bg-background"
                }`}
              >
                Sign in
              </a>
              <a
                href="/register"
                className="rounded-full bg-primary px-5 py-2.5 text-[0.6875rem] font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90"
              >
                Register
              </a>
            </>
          )}
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle navigation"
          className={`rounded-full border p-2.5 text-primary lg:hidden ${
            scrolled ? "border-border bg-surface" : "border-border/60 bg-background/50"
          }`}
        >
          {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </motion.div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="mx-auto max-w-[1400px] border-t border-border bg-background/95 px-5 pb-6 pt-4 backdrop-blur-xl lg:hidden"
          >
            <nav className="flex flex-col gap-4">
              {links.map((l) => (
                <a
                  key={l.label}
                  href={l.href}
                  onClick={() => setOpen(false)}
                  className="text-xs font-semibold uppercase tracking-[0.18em] text-secondary"
                >
                  {l.label}
                </a>
              ))}
            </nav>
            <div className="mt-6 flex flex-col gap-2.5">
              <a
                href="/signin"
                onClick={() => setOpen(false)}
                className="rounded-full border border-border bg-surface px-5 py-3 text-center text-xs font-semibold uppercase tracking-[0.16em] text-primary"
              >
                Sign in
              </a>
              <a
                href="/register"
                onClick={() => setOpen(false)}
                className="rounded-full bg-primary px-5 py-3 text-center text-xs font-semibold uppercase tracking-[0.16em] text-primary-foreground"
              >
                Register
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
