import { ref, watch } from "vue";

const STORAGE_KEY = "douban-theme";
const theme = ref(
  (typeof localStorage !== "undefined" && localStorage.getItem(STORAGE_KEY)) || "dark"
);

function apply(t) {
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("data-theme", t);
  }
}
apply(theme.value);

watch(theme, (t) => {
  apply(t);
  try { localStorage.setItem(STORAGE_KEY, t); } catch (e) { /* ignore */ }
});

export function useTheme() {
  function toggle() {
    theme.value = theme.value === "dark" ? "light" : "dark";
  }
  return { theme, toggle };
}
