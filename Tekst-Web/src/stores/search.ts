import {
  POST,
  type SearchResults,
  type SortingPreset,
  type SearchPagination,
  type ResourceSearchQuery,
} from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { Base64 } from 'js-base64';
import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStateStore } from './state';
import { usePlatformData } from '@/composables/platformData';

type GeneralSearchSettings = {
  pgn: SearchPagination;
  sort: SortingPreset;
  strict: boolean;
};

type QuickSearchSettings = {
  op: 'OR' | 'AND';
  re: boolean;
  txt?: string[];
};

type AdvancedSearchSettings = {};

type QuickSearchRequest = {
  type: 'quick';
  q: string;
  gen: GeneralSearchSettings;
  qck: QuickSearchSettings;
};

type AdvancedSearchRequest = {
  type: 'advanced';
  q: ResourceSearchQuery[];
  gen: GeneralSearchSettings;
  adv: AdvancedSearchSettings;
};

type SearchRequest = QuickSearchRequest | AdvancedSearchRequest;

const DEFAULT_SEARCH_SETTINGS = {
  gen: {
    pgn: { pg: 1, pgs: 10 },
    sort: 'relevance',
    strict: false,
  } as GeneralSearchSettings,
  qck: {
    op: 'OR',
    re: false,
  } as QuickSearchSettings,
  adv: {} as AdvancedSearchSettings,
};

const DEFAULT_SEARCH_REQUEST_BODY: QuickSearchRequest = {
  type: 'quick',
  q: '',
  gen: DEFAULT_SEARCH_SETTINGS.gen,
  qck: DEFAULT_SEARCH_SETTINGS.qck,
};

export const useSearchStore = defineStore('search', () => {
  const state = useStateStore();
  const { pfData } = usePlatformData();
  const router = useRouter();
  const { message } = useMessages();

  const settingsGeneral = ref<GeneralSearchSettings>(DEFAULT_SEARCH_SETTINGS.gen);
  const settingsQuick = ref<QuickSearchSettings>(DEFAULT_SEARCH_SETTINGS.qck);
  const settingsAdvanced = ref<AdvancedSearchSettings>(DEFAULT_SEARCH_SETTINGS.adv);
  const currentRequest = ref<SearchRequest>();

  const loading = ref(false);
  const error = ref(false);
  const results = ref<SearchResults>();

  const browseHits = ref(false);
  const browseCurrHit = ref<SearchResults['hits'][number]>();
  const browseHitIndexOnPage = ref(0);

  function encodeReqInUrl(requestBody?: SearchRequest): string | undefined {
    if (!requestBody) return undefined;
    try {
      return Base64.encode(JSON.stringify(requestBody), true);
    } catch {
      message.error($t('errors.unexpected'));
      return undefined;
    }
  }

  function decodeReqFromUrl(): SearchRequest {
    try {
      const q = router.currentRoute.value.query.q?.toString();
      const decoded: SearchRequest = q ? JSON.parse(Base64.decode(q)) : undefined;
      if (!decoded) throw new Error();
      settingsGeneral.value = decoded.gen || DEFAULT_SEARCH_SETTINGS.gen;
      settingsGeneral.value.pgn.pg = 1;
      settingsGeneral.value.pgn.pgs = 10;
      if (decoded.type === 'quick') {
        settingsQuick.value = decoded.qck || DEFAULT_SEARCH_SETTINGS.qck;
      } else if (decoded.type === 'advanced') {
        settingsAdvanced.value = decoded.adv || DEFAULT_SEARCH_SETTINGS.adv;
      } else {
        return DEFAULT_SEARCH_REQUEST_BODY;
      }
      return decoded;
    } catch {
      return DEFAULT_SEARCH_REQUEST_BODY;
    }
  }

  function _resetSearch() {
    browseHits.value = false;
    browseHitIndexOnPage.value = 0;
  }

  async function searchQuick(q: string) {
    _resetSearch();
    const req: QuickSearchRequest = {
      type: 'quick',
      q,
      gen: settingsGeneral.value,
      qck: settingsQuick.value,
    };
    gotoSearchResultsView(req);
    await _search(req);
  }

  async function searchAdvanced(q: ResourceSearchQuery[]) {
    _resetSearch();
    const req: AdvancedSearchRequest = {
      type: 'advanced',
      q,
      gen: settingsGeneral.value,
      adv: settingsAdvanced.value,
    };
    gotoSearchResultsView(req);
    await _search(req);
  }

  async function searchFromUrl() {
    _resetSearch();
    if (currentRequest.value) return;
    await _search(decodeReqFromUrl());
  }

  async function searchSecondary() {
    await _search({
      ...(currentRequest.value || DEFAULT_SEARCH_REQUEST_BODY),
      gen: settingsGeneral.value,
    });
  }

  function gotoSearchResultsView(
    req: SearchRequest = currentRequest.value || DEFAULT_SEARCH_REQUEST_BODY
  ) {
    router.push({
      name: 'searchResults',
      query: {
        q: encodeReqInUrl(req),
      },
    });
  }

  async function _search(req: SearchRequest) {
    loading.value = true;
    error.value = false;
    results.value = undefined;
    currentRequest.value = req;
    // search
    const { data, error: e } = await POST('/search', {
      body: req,
    });
    if (!e) {
      results.value = data;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  async function turnPage(direction: 'previous' | 'next'): Promise<boolean> {
    if (!results.value) return false;
    const currPage = settingsGeneral.value.pgn.pg;
    settingsGeneral.value.pgn.pg =
      direction === 'previous'
        ? Math.max(1, settingsGeneral.value.pgn.pg - 1)
        : Math.min(
            settingsGeneral.value.pgn.pg + 1,
            Math.floor(results.value.totalHits / settingsGeneral.value.pgn.pg) + 1
          );
    if (currPage !== settingsGeneral.value.pgn.pg) {
      await searchSecondary();
      return true;
    }
    return false;
  }

  async function browse() {
    if (!results.value || !currentRequest.value) return;
    browseHits.value = true;
    browseHitIndexOnPage.value = 0;
    browseCurrHit.value = results.value.hits[browseHitIndexOnPage.value];
    router.push({
      name: 'browse',
      params: {
        text: pfData.value?.texts.find((t) => t.id === browseCurrHit.value?.textId)?.slug || '',
      },
      query: { lvl: browseCurrHit.value.level, pos: browseCurrHit.value.position },
    });
  }

  async function browseSkipTo(direction: 'previous' | 'next'): Promise<boolean> {
    if (!results.value || !currentRequest.value) return false;
    const targetIndexOnPage = browseHitIndexOnPage.value + (direction === 'previous' ? -1 : 1);

    if (targetIndexOnPage < 0 && (await turnPage('previous'))) {
      browseHitIndexOnPage.value = settingsGeneral.value.pgn.pgs - 1;
    } else if (targetIndexOnPage >= results.value.hits.length && (await turnPage('next'))) {
      browseHitIndexOnPage.value = 0;
    } else {
      browseHitIndexOnPage.value = targetIndexOnPage;
    }

    browseCurrHit.value = results.value.hits[browseHitIndexOnPage.value];
    if (!browseCurrHit.value) return false;

    router.push({
      name: 'browse',
      params: {
        text: pfData.value?.texts.find((t) => t.id === browseCurrHit.value?.textId)?.slug || '',
      },
      query: { lvl: browseCurrHit.value?.level, pos: browseCurrHit.value?.position },
    });
    return true;
  }

  // set quick search settings text selection to all texts on working text change
  watch(
    () => state.text?.id,
    () => {
      settingsQuick.value.txt = pfData.value?.texts.map((t) => t.id);
    },
    { immediate: true }
  );

  return {
    settingsGeneral,
    settingsQuick,
    settingsAdvanced,
    searchQuick,
    searchAdvanced,
    searchFromUrl,
    searchSecondary,
    turnPage,
    gotoSearchResultsView,
    currentRequest,
    loading,
    error,
    results,
    browse,
    browseHits,
    browseHitIndexOnPage,
    browseCurrHit,
    browseSkipTo,
  };
});
