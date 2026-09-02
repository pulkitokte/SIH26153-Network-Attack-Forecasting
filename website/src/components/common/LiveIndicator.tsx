import { cn } from '../../utils/format';

interface Props {
  label?: string;
  online?: boolean;
  className?: string;
}

export function LiveIndicator({ label = 'Live monitoring', online = true, className }: Props) {
  return (
    <span className={cn('inline-flex items-center gap-2 text-xs text-mute', className)}>
      <span className="relative flex h-2.5 w-2.5">
        <span
          className={cn(
            'absolute inline-flex h-full w-full rounded-full opacity-60',
            online ? 'bg-safe live-dot' : 'bg-mute',
          )}
        />
        <span className={cn('relative inline-flex h-2.5 w-2.5 rounded-full', online ? 'bg-safe' : 'bg-mute')} />
      </span>
      {label}
    </span>
  );
}
