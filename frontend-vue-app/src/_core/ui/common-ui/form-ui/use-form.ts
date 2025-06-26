import type {
  BaseFormComponentType,
  ExtendedFormApi,
  ZayumFormProps,
} from './types';

import { defineComponent, h, isReactive, onBeforeUnmount, watch } from 'vue';

import { useStore } from '@/_core/shared/store';

import { FormApi } from './form-api';
import ZayumUseForm from './zayum-use-form.vue';

export function useZayumForm<
  T extends BaseFormComponentType = BaseFormComponentType,
>(options: ZayumFormProps<T>) {
  const IS_REACTIVE = isReactive(options);
  const api = new FormApi(options);
  const extendedApi: ExtendedFormApi = api as never;
  extendedApi.useStore = (selector) => {
    return useStore(api.store, selector);
  };

  const Form = defineComponent(
    (props: ZayumFormProps, { attrs, slots }) => {
      onBeforeUnmount(() => {
        api.unmount();
      });
      api.setState({ ...props, ...attrs });
      return () =>
        h(ZayumUseForm, { ...props, ...attrs, formApi: extendedApi }, slots);
    },
    {
      inheritAttrs: false,
      name: 'ZayumUseForm',
    },
  );
  // Add reactivity support
  if (IS_REACTIVE) {
    watch(
      () => options.schema,
      () => {
        api.setState({ schema: options.schema });
      },
      { immediate: true },
    );
  }

  return [Form, extendedApi] as const;
}
