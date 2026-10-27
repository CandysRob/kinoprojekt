import { onBeforeUnmount, ref, shallowRef } from "vue";

/**
 * Hoiab ühe päringu olekut: data, loading ja error.
 * Uus `run()` katkestab eelmise, et aeglane vana vastus ei kirjutaks uut üle.
 */
export function useRequest(request, { immediate = true } = {}) {
  const data = shallowRef(null);
  const error = ref(null);
  const loading = ref(false);
  let controller = null;

  async function run(...args) {
    controller?.abort();
    controller = new AbortController();
    const { signal } = controller;
    loading.value = true;
    error.value = null;
    try {
      const result = await request(...args, { signal });
      if (!signal.aborted) data.value = result;
    } catch (err) {
      if (err.name !== "AbortError") error.value = err;
    } finally {
      if (!signal.aborted) loading.value = false;
    }
  }

  onBeforeUnmount(() => controller?.abort());
  if (immediate) run();

  return { data, error, loading, run };
}
