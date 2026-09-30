export const useAuth = () => {
  const token = useCookie('auth_token', {
    maxAge: 60 * 60 * 24,
    sameSite: 'lax',
  });

  const isAuthenticated = computed(() => Boolean(token.value));

  const login = (accessToken: string) => {
    token.value = accessToken;
  };

  const logout = () => {
    token.value = null;
  };

  return {
    token,
    isAuthenticated,
    login,
    logout,
  };
};
