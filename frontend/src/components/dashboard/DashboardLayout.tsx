import { ReactNode } from "react";
import { Link, Outlet } from "@tanstack/react-router";
import { logout, getUser } from "@/lib/auth";

interface DashboardLayoutProps {
  children?: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const user = getUser();

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
            <a
              href="/dashboard"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Dashboard
            </a>
            <a
              href="/dashboard/emissions"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Emissions
            </a>
            <a
              href="/dashboard/leak-points"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Leak Points
            </a>
            <a
              href="/dashboard/recommendations"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Recommendations
            </a>
            <a
              href="/dashboard/simulations"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Simulations
            </a>
            <a
              href="/dashboard/settings"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-secondary hover:bg-mist hover:text-primary"
            >
              Settings
            </a>
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
                <p className="text-xs text-muted-foreground truncate">
                  {user?.email || ""}
                </p>
              </div>
            </div>
            <button
              onClick={logout}
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
            <h2 className="text-lg font-semibold text-primary">Dashboard</h2>
            <div className="flex items-center gap-4">
              {/* Factory Selector will be added here */}
              <div className="text-sm text-muted-foreground">
                Factory Selector
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  );
}
