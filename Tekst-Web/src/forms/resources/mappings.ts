import { type Component } from 'vue';
import DeepLLinksConfigFormItems from '@/forms/resources/DeepLLinksConfigFormItems.vue';

const specialConfigFormItems: Record<string, Component> = {
  deeplLinks: DeepLLinksConfigFormItems,
};

export default specialConfigFormItems;
