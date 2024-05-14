import { computed, ref } from 'vue';
import { DELETE, GET, POST } from '@/api';
import type { UserMessageCreate, UserMessageRead, UserMessageThread } from '@/api';
import { useAuthStore } from '@/stores';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { defineStore } from 'pinia';
import { useIntervalFn } from '@vueuse/core';

export const useUserMessagesStore = defineStore('userMessages', () => {
  const auth = useAuthStore();
  const { message } = useMessages();

  const { pause: stopThreadsPolling, resume: startThreadsPolling } = useIntervalFn(
    async () => {
      auth.user && (await loadThreads());
      unreadCount.value &&
        message.info($t('account.messages.msgUnreadCount', { count: unreadCount.value }));
    },
    30 * 1000, // 30 seconds
    { immediate: false, immediateCallback: true }
  );

  const threads = ref<UserMessageThread[]>([]);
  const loading = ref(false);
  const openThread = ref<UserMessageThread>();
  const showMessagingModal = ref(false);

  const unreadCount = computed<number>(() =>
    threads.value.map((t) => t.unread).reduce((a, b) => a + b, 0)
  );

  async function loadThreads() {
    loading.value = true;
    if (auth.user?.id) {
      const { data, error } = await GET('/messages/threads');
      if (!error) {
        threads.value = data;
      } else {
        threads.value = [];
      }
    } else {
      threads.value = [];
    }
    loading.value = false;
  }

  async function loadMessages(
    threadId: string | null | undefined = openThread.value?.id
  ): Promise<UserMessageRead[] | undefined> {
    threadId = threadId || null;
    loading.value = true;
    if (auth.user?.id) {
      const { data, error } = await GET('/messages', {
        params: { query: { thread: threadId } },
      });
      loading.value = false;
      if (!error) {
        const thread = threads.value.find((t) => t.id === threadId);
        if (thread) {
          thread.unread = 0;
        }
        return data;
      }
    }
    loading.value = false;
    return undefined;
  }

  async function send(msg: UserMessageCreate) {
    loading.value = true;
    const { data, error } = await POST('/messages', {
      body: msg,
    });
    loading.value = false;
    if (!error) {
      return data;
    } else {
      return null;
    }
  }

  async function deleteThread(id: string) {
    loading.value = true;
    const { error } = await DELETE('/messages/threads/{id}', {
      params: { path: { id } },
    });
    if (!error) {
      threads.value = threads.value.filter((t) => (id === 'system' ? !!t.id : t.id !== id));
      message.success($t('account.messages.deleteThreadSuccess'));
    }
    loading.value = false;
  }

  return {
    threads,
    openThread,
    loading,
    unreadCount,
    showMessagingModal,
    loadThreads,
    loadMessages,
    send,
    deleteThread,
    startThreadsPolling,
    stopThreadsPolling,
  };
});
