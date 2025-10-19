import { ComponentPropsWithoutRef, forwardRef } from 'react';
import { Button, Tooltip } from 'antd';

export type TooltipIconButtonProps = ComponentPropsWithoutRef<typeof Button> & {
  tooltip: string;
  side?: 'top' | 'bottom' | 'left' | 'right';
};

export const TooltipIconButton = forwardRef<
  HTMLButtonElement,
  TooltipIconButtonProps
>(({ children, tooltip, side = 'bottom', className, ...rest }, ref) => {
  return (
    <Tooltip title={tooltip} placement={side}>
      <Button
        type="text"
        size="small"
        {...rest}
        className={`size-6 p-1 ${className || ''}`}
        ref={ref}
      >
        {children}
        <span className="sr-only">{tooltip}</span>
      </Button>
    </Tooltip>
  );
});

TooltipIconButton.displayName = 'TooltipIconButton';
