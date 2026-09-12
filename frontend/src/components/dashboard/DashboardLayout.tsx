import { ReactNode, useEffect, useState, useRef } from "react";
import { Link, Outlet, useNavigate } from "@tanstack/react-router";
import { Building2, ChevronDown } from "lucide-react";
import { logout, getUser } from "@/lib/auth";
import { get } from "@/lib/api";
import { getSelectedFactoryId, setSelectedFactoryId } from "@/lib/factory";
import { ChatWidget } from "@/components/chat/ChatWidget";

interface DashboardLayoutProps {
  children?: ReactNode;
  title?: string;
  showAddFactoryButton?: boolean;
  onAddFactory?: () => void;
}

export function DashboardLayout({ children, title = "Dashboard", showAddFactoryButton = true, onAddFactory }: DashboardLayoutProps) {
  const user = getUser();
  const navigate = useNavigate();
  const [factories, setFactories] = useState<Array<{ id: string; name: string }>>([]);
  const [selectedFactoryId, setSelectedFactoryIdState] = useState<string | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    get("/api/v1/factories")
      .then(async (response) => {
        if (!response.ok) return;
        const data = await response.json();
        setFactories(data);
        const saved = getSelectedFactoryId();
        const selected = data.find((factory: { id: string }) => factory.id === saved) || data[0];
        if (selected) {
          setSelectedFactoryId(selected.id);
          setSelectedFactoryIdState(selected.id);
        }
      })
      .catch(() => undefined);
  }, []);

  const handleFactoryChange = (factoryId: string) => {
    setSelectedFactoryId(factoryId);
    setSelectedFactoryIdState(factoryId);
    window.dispatchEvent(new CustomEvent("factory-changed", { detail: factoryId }));
  };

  const handleLogout = () => {
    logout();
    navigate({ to: "/signin" });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-surface">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="border-b border-border px-6 py-4">
            <h1 className="text-xl font-semibold text-primary">CarbonLoop</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4">
            <Link
              to="/dashboard"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Dashboard
            </Link>
            <Link
              to="/dashboard/emissions"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Emissions
            </Link>
            <Link
              to="/dashboard/leak-points"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Leak Points
            </Link>
            <Link
              to="/dashboard/recommendations"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Recommendations
            </Link>
            <Link
              to="/dashboard/simulations"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Simulations
            </Link>
            <Link
              to="/dashboard/settings"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Settings
            </Link>
            {user?.role === "admin" && (
              <Link
                to="/admin"
                className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
              >
                Admin
              </Link>
            )}
          </nav>

          {/* User Info */}
          <div className="border-t border-border px-6 py-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-sm font-semibold text-primary">
                  {user?.fullName?.charAt(0) || "U"}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-primary truncate">
                  {user?.fullName || "User"}
                </p>
                <p className="text-xs text-muted-foreground truncate">{user?.email || ""}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="mt-3 w-full rounded-lg border border-border px-3 py-2 text-xs font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Sign Out
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="ml-64">
        {/* Header */}
        <header className="sticky top-0 z-30 border-b border-border bg-background/95 backdrop-blur">
          <div className="flex h-16 items-center justify-between px-6">
            <h2 className="text-lg font-semibold text-primary">{title}</h2>
            <div className="flex items-center gap-3">
              {factories.length > 0 && (
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="flex items-center gap-2 rounded-lg border border-border bg-surface px-4 py-2 text-sm font-medium text-primary hover:bg-mist transition-colors"
                  >
                    <Building2 className="h-4 w-4" />
                    <span className="max-w-[200px] truncate">
                      {factories.find((f) => f.id === selectedFactoryId)?.name || factories[0]?.name}
                    </span>
                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                  </button>
                  {isDropdownOpen && (
                    <div className="absolute right-0 top-full z-50 mt-2 w-64 rounded-lg border border-border bg-surface shadow-lg">
                      <div className="p-2">
                        {factories.map((factory) => (
                          <button
                            key={factory.id}
                            onClick={() => {
                              handleFactoryChange(factory.id);
                              setIsDropdownOpen(false);
                            }}
                            className={`w-full rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                              factory.id === selectedFactoryId
                                ? "bg-primary/10 text-primary font-medium"
                                : "text-secondary hover:bg-mist"
                            }`}
                          >
                            <div className="flex items-center gap-2">
                              <Building2 className="h-4 w-4 text-muted-foreground" />
                              <span className="truncate">{factory.name}</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {showAddFactoryButton && user?.role === "factory_owner" && (
                <button
                  type="button"
                  onClick={onAddFactory || (() => navigate({ to: "/dashboard/settings" }))}
                  className="rounded-full border border-border px-3 py-2 text-xs font-semibold uppercase tracking-[0.1em] text-secondary hover:bg-mist"
                >
                  Add factory
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">{children || <Outlet />}</main>
      </div>

      {/* Chat Widget */}
      <ChatWidget />
    </div>
  );
}
