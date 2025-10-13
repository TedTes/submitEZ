'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Features', href: '/#how-it-works' },
  { name: 'Benefits', href: '/#benefits' },
  { name: 'Pricing', href: '/#pricing' },
]

export function MarketingHeader() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        {/* Logo - Links to landing page */}
        <Link href="/" className="flex items-center space-x-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white font-bold text-xl">
            S
          </div>
          <span className="hidden font-bold sm:inline-block text-xl">
            SubmitEZ
          </span>
        </Link>

        {/* Marketing Navigation */}
        <nav className="flex items-center space-x-6 ml-8">
          {navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'text-sm font-medium transition-colors hover:text-primary',
                pathname === item.href
                  ? 'text-foreground'
                  : 'text-muted-foreground'
              )}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="ml-auto flex items-center space-x-4">
          {/* Sign In link - future */}
          {/* <Link href="/signin">
            <Button variant="ghost">Sign In</Button>
          </Link> */}
          
          <Link href="/dashboard">
            <Button>Launch App</Button>
          </Link>
        </div>
      </div>
    </header>
  )
}