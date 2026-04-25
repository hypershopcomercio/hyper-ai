import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Routes that don't require authentication
const publicRoutes = ['/login', '/api'];

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Allow public routes
    if (publicRoutes.some(route => pathname.startsWith(route))) {
        return NextResponse.next();
    }

    // Allow static files
    if (pathname.startsWith('/_next') || pathname.startsWith('/favicon') || pathname.includes('.')) {
        return NextResponse.next();
    }

    // Check for auth token in cookies or headers
    const token = request.cookies.get('token')?.value;

    // For client-side auth, we'll check in the component
    // This middleware just ensures the login page exists as entry point

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!_next/static|_next/image|favicon.ico).*)']
};
