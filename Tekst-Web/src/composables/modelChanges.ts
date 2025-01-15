import { computed, ref, type Ref } from 'vue';

export function useModelChanges(model: Ref<Record<string, unknown> | undefined>) {
  const beforeEntriesJson = ref(valuesToJSON(model.value));
  const afterEntriesJson = computed(() => valuesToJSON(model.value));
  const changed = computed(() =>
    Object.entries(afterEntriesJson.value).some(([k, v]) => v !== beforeEntriesJson.value[k])
  );

  function valuesToJSON(o: Record<string, unknown> | undefined) {
    return Object.fromEntries(Object.entries(o || {}).map(([k, v]) => [k, JSON.stringify(v)]));
  }

  function getChanges() {
    if (!changed.value) {
      return {};
    } else {
      return Object.fromEntries(
        Object.entries(afterEntriesJson.value)
          .filter(([k, v]) => v !== beforeEntriesJson.value[k])
          .map(([k, v]) => [k, JSON.parse(v)])
      );
    }
  }

  function reset() {
    beforeEntriesJson.value = valuesToJSON(model.value);
  }

  return {
    changed,
    getChanges,
    reset,
  };
}
