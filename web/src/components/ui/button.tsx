import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva('inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium transition', {
  variants: {
    variant: {
      default: 'bg-primary text-white hover:opacity-90',
      outline: 'border border-border bg-card hover:bg-stone-100',
      ghost: 'hover:bg-stone-100',
    },
  },
  defaultVariants: { variant: 'default' },
});

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export function Button({ className, variant, asChild = false, type, children, ...props }: ButtonProps) {
  const classes = cn(buttonVariants({ variant }), className);

  if (asChild && React.isValidElement(children)) {
    const childProps = children.props as { className?: string };
    return React.cloneElement(children, {
      ...props,
      className: cn(classes, childProps.className),
    });
  }

  return (
    <button type={type ?? 'button'} className={classes} {...props}>
      {children}
    </button>
  );
}
