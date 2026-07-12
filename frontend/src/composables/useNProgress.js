// 极简 NProgress: 单一元素 + 三种状态(show / done / hidden)
let el = null;
let hideTimer = null;

function ensure() {
  if (el) return el;
  el = document.createElement("div");
  el.className = "np-bar";
  document.body.appendChild(el);
  return el;
}

export function useNProgress() {
  function start() {
    const bar = ensure();
    bar.classList.remove("done");
    bar.classList.add("show");
    clearTimeout(hideTimer);
  }
  function done() {
    if (!el) return;
    el.classList.remove("show");
    el.classList.add("done");
    hideTimer = setTimeout(() => el && el.classList.remove("done"), 450);
  }
  return { start, done };
}
