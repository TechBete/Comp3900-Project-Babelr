import {NextResponse, NextRequest} from 'next/server';

const PUBLIC_PATHS = [
    '/Auth/login',
    '/Auth/register_listener',
    '/Auth/register_researcher',
    '/Auth/reset_password'
  ];

export const config = {
    matcher: [
      '/Listener/:path*',
      '/Researcher/:path*',
      '/app/:path*'
    ],
  };

const isDev = process.env.NODE_ENV === 'development';

const baseURL = isDev
  ? 'http://localhost:8016' // your local machine
  : 'http://web:8016';      // Docker-internal service

export async function middleware(req: NextRequest) {
    const token = req.cookies.get('access_token_cookie')?.value;
    const {pathname} = req.nextUrl;
    
    if (PUBLIC_PATHS.some(path => pathname.startsWith(path))) {
        return NextResponse.next();
      }

    if (!token) {
        return NextResponse.redirect(new URL('/Auth/login', req.url));
    }
    try {

        if (pathname.startsWith('/Listener') || pathname.startsWith('/Researcher')) {
            const res = await fetch(`${baseURL}/auth/getRoleFromID`, {
                method: 'GET',
                headers: {
                  Cookie: req.headers.get('cookie') || '',
                },
              });

            const data = await res.json();

            if (data.error || !data.role) {
                return NextResponse.redirect(new URL('/unauthorised1', req.url));
            }
            

            if (
                (pathname.startsWith('/Listener') && data.role !== 'listener') ||
                (pathname.startsWith('/Researcher') && data.role !== 'researcher')
            ) {
                return NextResponse.redirect(new URL('/unauthorised2', req.url));
            }
        }

        return NextResponse.next();
    } catch (e) {
        console.error('Role API check failed: ', e)
        return NextResponse.redirect(new URL('/unauthorised3', req.url));
    }
}

