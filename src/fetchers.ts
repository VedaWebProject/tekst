import { ref, isRef, unref, watchEffect, type Ref } from 'vue';
import { configureApi } from './openApiConfig';
import {
  PlatformApi,
  AdminApi,
  type UserReadPublic,
  type PlatformStats,
  type UserRead,
} from '@/openapi';
import type { AxiosResponse } from 'axios';

export function useProfile(username: string | Ref) {
  const user = ref<UserReadPublic | null>(null);
  const error = ref(false);
  const platformApi = configureApi(PlatformApi);

  function fetchProfileData() {
    user.value = null;
    error.value = false;
    platformApi
      .getPublicUserInfo({ username: unref(username) })
      .then((response: AxiosResponse<UserReadPublic, any>) => response.data)
      .then((u: UserReadPublic) => (user.value = u))
      .catch(() => (error.value = true));
  }

  if (isRef(username)) {
    watchEffect(fetchProfileData);
  } else {
    fetchProfileData();
  }

  return { user, error };
}

export function useStats() {
  const stats = ref<PlatformStats | null>(null);
  const error = ref(false);
  const adminApi = configureApi(AdminApi);

  function load() {
    stats.value = null;
    error.value = false;
    adminApi
      .getStats()
      .then((response: AxiosResponse<PlatformStats, any>) => response.data)
      .then((s: PlatformStats) => (stats.value = s))
      .catch(() => (error.value = true));
  }

  load();

  return { stats, error, load };
}

export function useUsers() {
  const users = ref<Array<UserRead> | null>(null);
  const error = ref(false);
  const adminApi = configureApi(AdminApi);

  function load() {
    users.value = null;
    error.value = false;
    adminApi
      .getUsers()
      .then((response: AxiosResponse<Array<UserRead>, any>) => response.data)
      .then((u: Array<UserRead>) => (users.value = u))
      .catch(() => (error.value = true));
  }

  load();

  return {
    users,
    error,
    load,
  };
}
