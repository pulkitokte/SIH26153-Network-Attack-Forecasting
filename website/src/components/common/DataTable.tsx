import type { ReactNode } from 'react';
import { cn } from '../../utils/format';

interface Column<T> {
  key: string;
  header: string;
  className?: string;
  render: (row: T) => ReactNode;
}

interface Props<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  dense?: boolean;
}

export function DataTable<T>({ columns, rows, rowKey, dense }: Props<T>) {
  return (
    <div className="overflow-x-auto scrollbar-thin">
      <table className="w-full min-w-[720px] text-left text-sm">
        <thead>
          <tr className="border-b border-white/8 text-[11px] uppercase tracking-[0.14em] text-mute">
            {columns.map((col) => (
              <th key={col.key} className={cn('px-3 py-3 font-medium', col.className)}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={rowKey(row)} className="border-b border-white/5 hover:bg-white/[0.03]">
              {columns.map((col) => (
                <td key={col.key} className={cn(dense ? 'px-3 py-2' : 'px-3 py-3', 'text-ink/90', col.className)}>
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
