import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;
    const token = request.cookies.get('token')?.value;

    // Se estiver na raiz, manda para o dashboard ou login
    if (pathname === '/') {
        return NextResponse.redirect(new URL(token ? '/perform/analytics' : '/login', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico|logo.*\\.png).*)'],
};
