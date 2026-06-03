import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;
    const token = request.cookies.get('auth_token')?.value;
    const isAuthBypass = process.env.NEXT_PUBLIC_AUTH_BYPASS === 'true';

    // Se estiver na raiz /, redireciona
    if (pathname === '/') {
        return NextResponse.redirect(new URL((token || isAuthBypass) ? '/perform/analytics' : '/login', request.url));
    }

    // Se NÃO tem token e NÃO está na página de login, expulsa para o login
    if (!token && !isAuthBypass && pathname !== '/login') {
        return NextResponse.redirect(new URL('/login', request.url));
    }

    // Se TEM token e tenta entrar no login, manda para o dashboard
    if ((token || isAuthBypass) && pathname === '/login') {
        return NextResponse.redirect(new URL('/perform/analytics', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico|logo.*\\.png).*)'],
};
