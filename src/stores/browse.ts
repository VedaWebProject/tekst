import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useMessagesStore, useStateStore } from '@/stores';
import type { NodeRead } from '@/openapi';
import { LayersApi, NodesApi, UnitsApi } from '@/openapi/api';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const route = useRoute();
  const router = useRouter();
  const messages = useMessagesStore();

  // API clients
  const nodesApi = new NodesApi();
  const layersApi = new LayersApi();
  const unitsApi = new UnitsApi();

  /* BROWSE UI CONTROLS */

  const showLayerToggleDrawer = ref(false);
  const condensedView = ref(false);

  /* BROWSE NODE PATH */

  const nodePath = ref<NodeRead[]>([]);
  const nodePathHead = computed(() =>
    nodePath.value.length > 0 ? nodePath.value[nodePath.value.length - 1] : undefined
  );
  const nodePathRoot = computed(() => (nodePath.value.length > 0 ? nodePath.value[0] : undefined));
  const level = computed(() =>
    nodePathHead.value?.level !== undefined
      ? nodePathHead.value.level
      : state.text?.defaultLevel || 0
  );
  const position = computed(() => nodePathHead.value?.position);

  // update browse node path
  async function updateBrowseNodePath() {
    if (route.name === 'browse') {
      const qLvl = parseInt(route.query.lvl?.toString() || '') ?? 0;
      const qPos = parseInt(route.query.pos?.toString() || '') ?? 0;
      if (Number.isInteger(qLvl) && Number.isInteger(qPos)) {
        try {
          // fill browse node path up to root (no more parent)
          const path = await nodesApi
            .getPathByHeadLocation({
              textId: state.text?.id || '',
              level: qLvl,
              position: qPos,
            })
            .then((response) => response.data);
          if (!path || path.length == 0) {
            throw new Error();
          }
          nodePath.value = path;
        } catch {
          resetBrowseLocation(level.value);
        }
      } else {
        resetBrowseLocation();
      }
    }
  }

  // reset browse location (change URI parameters)
  function resetBrowseLocation(
    level: number = state.text?.defaultLevel || 0,
    position: number = 0
  ) {
    router.replace({
      ...route,
      query: {
        ...route.query,
        lvl: level,
        pos: position,
      },
    });
  }

  // set browse location to text default when text changes
  watch(
    () => state.text,
    () => route.name === 'browse' && resetBrowseLocation()
  );

  // react to route changes concerning browse state
  watch(route, (after, before) => {
    if (after.name === 'browse' && after.params.text === before.params.text) {
      updateBrowseNodePath();
    }
  });

  /* BROWSE LAYERS AND UNITS */

  const layers = ref<Record<string, any>[]>([]);

  async function loadLayersData() {
    if (!state.text) return;
    // set all layers to loading
    layers.value.forEach((l) => {
      l.loading = true;
    });
    // fetch data
    try {
      // fetch layers data
      const layersData = await layersApi
        .findLayers({ textId: state.text.id })
        .then((response) => response.data);
      layersData.forEach((l: Record<string, any>) => {
        // keep layer deactivated if it was before
        const existingLayer = layers.value.find((lo) => lo.id === l.id);
        l.active = !existingLayer || existingLayer.active;
        l.loading = false;
      });
      loadUnitsData(layersData);
    } catch (e) {
      console.error(e);
      messages.error('Error loading data layers for this location');
    }
  }

  async function loadUnitsData(layersData = layers.value) {
    if (!nodePathHead.value) return;
    // set all layers to loading
    layers.value.forEach((l) => {
      l.loading = true;
    });
    try {
      // fetch untis data
      const unitsData = await unitsApi
        .findUnits({ nodeId: [nodePathHead.value.id] })
        .then((response) => response.data);
      // assign units to layers
      layersData.forEach((l: Record<string, any>) => {
        l.unit = unitsData.find((u: Record<string, any>) => u.layerId == l.id);
        l.loading = false;
      });
      // assign (potentially) fresh layers/untis data to store prop
      layers.value = layersData;
    } catch (e) {
      console.error(e);
      messages.error('Error loading data layer units for this location');
    }
  }

  // load layers/units data on browse location change
  watch(
    () => nodePathHead.value,
    (after: NodeRead | undefined, before: NodeRead | undefined) => {
      if (after?.textId === before?.textId) {
        // selected text didn't change, only the location did,
        // so it's enough to load new units data
        loadUnitsData();
      } else {
        // node path head changed because a different text was selected,
        // so we have to load full layers data AND according units data
        loadLayersData();
      }
    }
  );

  return {
    showLayerToggleDrawer,
    condensedView,
    layers,
    nodePath,
    nodePathHead,
    nodePathRoot,
    level,
    position,
    updateBrowseNodePath,
    resetBrowseLocation,
    loadLayersData,
  };
});
