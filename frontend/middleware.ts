import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

import { authenticationMiddlewarePlaceholder } from '@/lib/middleware/auth';
import { authorizationMiddlewarePlaceholder } from '@/lib/middleware/authorization';
import { maintenanceModeMiddlewarePlaceholder } from '@/lib/middleware/maintenance-mode';

export function middleware(_request: NextRequest) {
  const isAuthenticated = authenticationMiddlewarePlaceholder();
  const isAuthorized = authorizationMiddlewarePlaceholder('viewer');
  const maintenanceMode = maintenanceModeMiddlewarePlaceholder();

  if (!isAuthenticated || !isAuthorized || maintenanceMode) {
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
