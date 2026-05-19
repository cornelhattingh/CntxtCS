import { useLocation } from 'react-router-dom'

const titles: Record<string, string> = {
  '/': 'Dashboard',
  '/graph': 'Graph',
  '/explorer': 'Explorer',
}

export function PageTitle() {
  const { pathname } = useLocation()
  const title = titles[pathname] ?? 'CntxtCS'
  return (
    <span className="text-sm font-medium text-foreground">{title}</span>
  )
}
