// 极简 NProgress：单一元素 + 三种状态(show / done / hidden)
// 设计：
//  - start() 标记为显示，但若 200ms 内完成也至少撑到 200ms，避免快请求闪烁
//  - done() 进入完成态后 600ms 淡出，避免快速切换时进度条抖
//  - 通过 inc(n) 可渐进推进（多请求并发时调用，0-1 之间）
import { ref, readonly } from "vue";

let el = null;
let hideTimer = null;
let minShowTimer = null;
let startedAt = 0;
const pending = ref(0);
const visible = ref(false);

const MIN_SHOW_MS = 200;
const DONE_FADE_MS = 600;

function ensure() {
  if (el) return el;
  el = document.createElement("div");
  el.className = "np-bar";
  document.body.appendChild(el);
  return el;
}

function clearTimers() {
  if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  if (minShowTimer) { clearTimeout(minShowTimer); minShowTimer = null; }
}

export function useNProgress() {
  function start() {
    const bar = ensure();
    clearTimers();
    bar.classList.remove("done");
    bar.classList.add("show");
    startedAt = Date.now();
    visible.value = true;
  }

  function inc(n = 0.2) {
    // 渐进推进：仅在显示中追加可见位移
    if (!el || !visible.value) return;
    const cur = parseFloat(el.style.getPropertyValue("--np-progress") || "0");
    const next = Math.min(0.95, cur + n);
    el.style.setProperty("--np-progress", String(next));
    el.style.transform = `scaleX(${next})`;
  }

  function done() {
    if (!el) return;
    const elapsed = Date.now() - startedAt;
    if (elapsed < MIN_SHOW_MS) {
      // 请求太快，等到 MIN_SHOW_MS 再完成
      minShowTimer = setTimeout(() => actuallyDone(), MIN_SHOW_MS - elapsed);
      return;
    }
    actuallyDone();
  }

  function actuallyDone() {
    if (!el) return;
    el.classList.remove("show");
    el.classList.add("done");
    visible.value = false;
    pending.value = 0;
    hideTimer = setTimeout(() => {
      if (!el) return;
      el.classList.remove("done");
      el.style.removeProperty("--np-progress");
      el.style.removeProperty("transform");
    }, DONE_FADE_MS);
  }

  return { start, done, inc, visible: readonly(visible) };
}
