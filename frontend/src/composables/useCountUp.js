import { ref, watch, onUnmounted } from "vue";

// 1.5s easeOutCubic 数字滚动;尊重 prefers-reduced-motion
export function useCountUp(source, { duration = 1500, decimals = 0, immediate = true } = {}) {
  const value = ref(immediate ? 0 : (Number(source.value) || 0));
  let raf = 0;
  let from = 0;
  let to = Number(source.value) || 0;
  let started = 0;

  const ease = (t) => 1 - Math.pow(1 - t, 3);

  const reduceMotion =
    typeof window !== "undefined" &&
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function render(now) {
    const t = Math.min(1, (now - started) / duration);
    const cur = from + (to - from) * ease(t);
    value.value = decimals > 0 ? Number(cur.toFixed(decimals)) : Math.round(cur);
    if (t < 1) raf = requestAnimationFrame(render);
  }

  function play(newVal) {
    cancelAnimationFrame(raf);
    to = Number(newVal) || 0;
    if (reduceMotion) { value.value = to; return; }
    from = value.value;
    started = performance.now();
    raf = requestAnimationFrame(render);
  }

  watch(source, (v) => play(v), { immediate });

  onUnmounted(() => cancelAnimationFrame(raf));
  return value;
}
