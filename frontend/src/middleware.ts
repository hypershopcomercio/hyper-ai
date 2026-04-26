import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;
    const token = request.cookies.get('auth_token')?.value;

    // Se estiver na raiz /, redireciona
    if (pathname === '/') {
        return NextResponse.redirect(new URL(token ? '/perform/analytics' : '/login', request.url));
    }

    // Se NÃO tem token e NÃO está na página de login, expulsa para o login
    if (!token && pathname !== '/login') {
        return NextResponse.redirect(new URL('/login', request.url));
    }

    // Se TEM token e tenta entrar no login, manda para o dashboard
    if (token && pathname === '/login') {
        return NextResponse.redirect(new URL('/perform/analytics', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico|logo.*\\.png).*)'],
};
