import { useState, type ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useSimulation } from '../../context/SimulationContext';
import { AlertTriangle } from 'lucide-react';

export function AppLayout({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const { banner } = useSimulation();

  return (
    <div className="soc-shell flex min-h-screen">
      <div className="hidden lg:block">
        <div className="sticky top-0 h-screen">
          <Sidebar />
        </div>
      </div>
      {open ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button className="absolute inset-0 bg-black/60" aria-label="Close menu" onClick={() => setOpen(false)} />
          <div className="relative h-full w-[260px]">
            <Sidebar onNavigate={() => setOpen(false)} />
          </div>
        </div>
      ) : null}
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenu={() => setOpen(true)} />
        {banner ? (
          <div className="flex items-center gap-2 border-b border-critical/25 bg-critical/10 px-4 py-2 text-sm text-critical lg:px-6">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {banner}
          </div>
        ) : null}
        <main className="soc-grid flex-1 overflow-x-hidden p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}
