import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

function Icon({ children, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width="20"
      height="20"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...props}
    >
      {children}
    </svg>
  )
}

export const HomeIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 10.5 12 3l9 7.5" />
    <path d="M5 9.5V21h14V9.5" />
    <path d="M10 21v-6h4v6" />
  </Icon>
)

export const MapIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m9 4-6 2.5v13L9 17l6 2.5 6-2.5v-13L15 6.5 9 4Z" />
    <path d="M9 4v13M15 6.5v13" />
  </Icon>
)

export const RankIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />
  </Icon>
)

export const BriefIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M7 3h7l5 5v13H7z" />
    <path d="M14 3v5h5M10 13h6M10 17h6" />
  </Icon>
)

export const BookIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z" />
    <path d="M4 19V5M9 7h6" />
  </Icon>
)

export const CheckIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m5 12.5 4.5 4.5L19 7.5" />
  </Icon>
)

export const AlertIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 3 2.5 20h19z" />
    <path d="M12 10v4.5M12 17.5v.01" />
  </Icon>
)

export const CompassMark = (p: IconProps) => (
  <svg viewBox="0 0 32 32" width="34" height="34" aria-hidden="true" focusable="false" {...p}>
    <defs>
      <linearGradient id="cm" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#a29bfe" />
        <stop offset="1" stopColor="#7552e0" />
      </linearGradient>
    </defs>
    <rect width="32" height="32" rx="10" fill="url(#cm)" />
    <circle cx="16" cy="16" r="8.5" fill="none" stroke="#fff" strokeOpacity=".7" strokeWidth="1.6" />
    <path d="m19.8 12.2-2.4 5.2-5.2 2.4 2.4-5.2z" fill="#fff" />
  </svg>
)
