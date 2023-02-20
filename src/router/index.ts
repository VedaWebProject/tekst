import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore, useMessagesStore } from '@/stores';
import { HomeView, AboutView, AccountView, LoginView, RegisterView } from '@/views';
import { i18n } from '@/i18n';

// restricted routes
const ONLY_USERS = ['/account'];
const ONLY_SUPERUSERS = ['/admin'];

const t = i18n.global.t;

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'active',
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/account',
      name: 'account',
      component: AccountView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: HomeView,
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  const messages = useMessagesStore();
  // assess auth situation
  const ru = ONLY_USERS.includes(to.path); // route is restricted to users
  const rsu = ONLY_SUPERUSERS.includes(to.path); // route is restricted to to superusers
  const l = auth.loggedIn; // a user is logged in
  const u = auth.user?.isActive; // the user is a verified, active user
  const su = auth.user?.isSuperuser; // the user is a superuser
  const authorized = !(ru || rsu) || (ru && l && u) || (rsu && l && su);
  // redirect if trying to access a restricted page without aithorization
  if (!authorized) {
    auth.returnUrl = to.fullPath;
    messages.warning(t('errors.noAccess', { resource: to.path }));
    return '/home';
  }
});

export default router;
