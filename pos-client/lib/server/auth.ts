'use server';

import { cookies } from 'next/headers';
import { serverSubmit } from './api';

/**
 * Server-side login action
 */
export async function loginAction(credentials: { username: string; password: string }) {
  const response = await serverSubmit<{ access: string; refresh: string }>(
    '/auth/users/login/',
    'POST',
    credentials
  );

  if (response.data) {
    // Set HTTP-only cookies
    (await
          // Set HTTP-only cookies
          cookies()).set('accessToken', response.data.access, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60, // 1 hour
    });
    
    (await cookies()).set('refreshToken', response.data.refresh, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60 * 24 * 7, // 7 days
    });
  }

  return response;
}

/**
 * Server-side logout action
 */
export async function logoutAction() {
  // Clear auth cookies
  (await
        // Clear auth cookies
        cookies()).delete('accessToken');
  (await cookies()).delete('refreshToken');
  
  // Optional: Invalidate token on server
  await serverSubmit('/auth/logout/', 'POST', {});
  
  return { success: true };
}