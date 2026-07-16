import { cn } from '@/lib/utils';

interface ProgressProps {
  value?: number;       // 0–100
  className?: string;
  indicatorClassName?: string;
}

/**
 * Simple progress bar component (no Radix dependency).
 * Accessible via role="progressbar" and aria attributes.
 */
function Progress({ value = 0, className, indicatorClassName }: ProgressProps) {
  const clamped = Math.min(100, Math.max(0, value));
  return (
    <div
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
      className={cn(
        'relative h-2 w-full overflow-hidden rounded-full bg-muted',
        className,
      )}
    >
      <div
        className={cn('h-full rounded-full bg-primary transition-all', indicatorClassName)}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}

export { Progress };
