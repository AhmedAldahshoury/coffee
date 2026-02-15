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

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant }), className)} {...props} />;
}
