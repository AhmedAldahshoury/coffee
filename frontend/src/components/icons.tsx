import { ReactNode, SVGProps } from 'react';

interface IconProps extends SVGProps<SVGSVGElement> {
  size?: number;
}

function IconBase({ size = 18, children, ...props }: IconProps & { children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  );
}

export function LogoMark({ size = 28, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true" {...props}>
      <defs>
        <linearGradient id="caramel" x1="6" y1="3" x2="27" y2="28" gradientUnits="userSpaceOnUse">
          <stop stopColor="var(--accent-300)" />
          <stop offset="1" stopColor="var(--accent-500)" />
        </linearGradient>
      </defs>
      <path d="M15.5 5.5C20 10.4 22 14.6 22 18.3C22 22.8 19.1 26 15.5 26C11.9 26 9 22.8 9 18.3C9 14.6 11 10.4 15.5 5.5Z" fill="url(#caramel)" />
      <circle cx="22.8" cy="10" r="2.2" fill="var(--teal-500)" />
      <path d="M22.8 12.2V16.5" stroke="var(--teal-500)" strokeWidth="1.6" />
      <path d="M20.6 14.2H25" stroke="var(--teal-500)" strokeWidth="1.6" />
    </svg>
  );
}

export function HomeIcon(props: IconProps) { return <IconBase {...props}><path d="M3 10.5L12 3l9 7.5" /><path d="M5.5 9.5V20h13V9.5" /></IconBase>; }
export function TrophyIcon(props: IconProps) { return <IconBase {...props}><path d="M7 4h10v4a5 5 0 0 1-10 0V4Z" /><path d="M10 18h4" /><path d="M8.5 21h7" /><path d="M17 6h2a2 2 0 0 1 0 4h-2" /><path d="M7 6H5a2 2 0 0 0 0 4h2" /></IconBase>; }
export function UserIcon(props: IconProps) { return <IconBase {...props}><circle cx="12" cy="8" r="3" /><path d="M5 20a7 7 0 0 1 14 0" /></IconBase>; }
export function MoonIcon(props: IconProps) { return <IconBase {...props}><path d="M20 14.5A7.5 7.5 0 1 1 9.5 4 6 6 0 0 0 20 14.5Z" /></IconBase>; }
export function SunIcon(props: IconProps) { return <IconBase {...props}><circle cx="12" cy="12" r="4" /><path d="M12 2.8v2.4M12 18.8v2.4M21.2 12h-2.4M5.2 12H2.8M18.8 5.2l-1.7 1.7M7 17l-1.8 1.8M18.8 18.8 17 17M7 7 5.2 5.2" /></IconBase>; }
export function LogoutIcon(props: IconProps) { return <IconBase {...props}><path d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4" /><path d="M14 16l4-4-4-4" /><path d="M18 12H9" /></IconBase>; }
export function BoltIcon(props: IconProps) { return <IconBase {...props}><path d="M13 2 6 13h5l-1 9 8-12h-5l0-8Z" /></IconBase>; }
export function SparkIcon(props: IconProps) { return <IconBase {...props}><path d="m12 3 1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8L12 3Z" /><path d="m19 15 .9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9L19 15Z" /></IconBase>; }
export function ChevronIcon(props: IconProps) { return <IconBase {...props}><path d="m9 6 6 6-6 6" /></IconBase>; }
export function CheckIcon(props: IconProps) { return <IconBase {...props}><path d="M5 13l4 4L19 7" /></IconBase>; }
export function CoffeeIcon(props: IconProps) { return <IconBase {...props}><path d="M4 8h12v6a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4V8Z" /><path d="M16 10h2a2 2 0 0 1 0 4h-2" /><path d="M7 4c.7.7.7 1.6 0 2.3M10 4c.7.7.7 1.6 0 2.3" /></IconBase>; }
export function PlayIcon(props: IconProps) { return <IconBase {...props}><path d="M8 6v12l10-6-10-6Z" /></IconBase>; }
export function PauseIcon(props: IconProps) { return <IconBase {...props}><path d="M8 6v12M16 6v12" /></IconBase>; }
export function RotateIcon(props: IconProps) { return <IconBase {...props}><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v4h4" /></IconBase>; }
export function TimerIcon(props: IconProps) { return <IconBase {...props}><circle cx="12" cy="13" r="8" /><path d="M12 13V9" /><path d="M9 2h6" /></IconBase>; }
export function NoteIcon(props: IconProps) { return <IconBase {...props}><path d="M5 4h14v16H5z" /><path d="M8 9h8M8 13h8M8 17h5" /></IconBase>; }
export function TagIcon(props: IconProps) { return <IconBase {...props}><path d="M12 3H5v7l9 9 7-7-9-9Z" /><circle cx="8" cy="8" r="1" /></IconBase>; }
