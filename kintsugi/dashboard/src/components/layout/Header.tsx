import { useLocation } from 'react-router-dom'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { Separator } from '@/components/ui/separator'

export function Header() {
  const location = useLocation()

  const pageTitles: Record<string, string> = {
    '/': 'Dashboard',
    '/submit': 'Submit Problem',
  }

  const title = pageTitles[location.pathname] || 'HiveMind'

  return (
    <header className="flex h-14 items-center gap-3 border-b px-4">
      <SidebarTrigger />
      <Separator orientation="vertical" className="h-5" />
      <h1 className="text-base font-medium tracking-tight">{title}</h1>
    </header>
  )
}
