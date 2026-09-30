import init, { HwpDocument } from './rhwp.js';

let measureContext = null;
globalThis.measureTextWidth = (font, value) => {
  if (!measureContext) measureContext = document.createElement('canvas').getContext('2d');
  measureContext.font = font;
  return measureContext.measureText(value).width;
};

const leftState = { side: 'left', doc: null, page: 0, total: 0, zoom: 1 };
const rightState = { side: 'right', doc: null, page: 0, total: 0, zoom: 1 };
const wasmReady = init({ module_or_path: new URL('./rhwp_bg.wasm', import.meta.url) });

function decodeBase64(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

function updateControls(state) {
  document.getElementById(`${state.side}-page`).textContent = state.total ? `${state.page + 1} / ${state.total}` : '- / -';
  document.getElementById(`${state.side}-zoom`).textContent = `${Math.round(state.zoom * 100)}%`;
  document.getElementById(`${state.side}-prev`).disabled = state.page <= 0;
  document.getElementById(`${state.side}-next`).disabled = state.page >= state.total - 1;
}

function render(state) {
  const view = document.getElementById(`${state.side}-view`);
  try {
    view.innerHTML = `<div class="page-shell"><div class="page">${state.doc.renderPageSvg(state.page)}</div></div>`;
    const page = view.querySelector('.page');
    const shell = view.querySelector('.page-shell');
    const svg = page.querySelector('svg');
    const width = Number.parseFloat(svg.getAttribute('width')) || svg.getBoundingClientRect().width;
    const height = Number.parseFloat(svg.getAttribute('height')) || svg.getBoundingClientRect().height;
    shell.style.width = `${width * state.zoom}px`;
    shell.style.height = `${height * state.zoom}px`;
    page.style.width = `${width}px`;
    page.style.height = `${height}px`;
    page.style.transform = `scale(${state.zoom})`;
    document.getElementById(`${state.side}-status`).textContent = '표시 완료';
    updateControls(state);
  } catch (error) {
    view.innerHTML = `<div class="error">페이지를 표시하지 못했습니다.<br>${String(error)}</div>`;
    document.getElementById(`${state.side}-status`).textContent = '오류';
  }
}

async function loadOne(state, encoded, name) {
  const view = document.getElementById(`${state.side}-view`);
  document.getElementById(`${state.side}-name`).textContent = name;
  document.getElementById(`${state.side}-status`).textContent = '불러오는 중';
  try {
    if (state.doc) state.doc.free();
    state.doc = new HwpDocument(decodeBase64(encoded));
    state.page = 0; state.zoom = 1; state.total = state.doc.pageCount();
    if (state.total < 1) throw new Error('표시할 페이지가 없습니다.');
    render(state);
  } catch (error) {
    state.doc = null; state.total = 0;
    view.innerHTML = `<div class="error">문서를 열지 못했습니다.<br>${String(error)}</div>`;
    document.getElementById(`${state.side}-status`).textContent = '오류';
    updateControls(state);
  }
}

function bind(state) {
  document.getElementById(`${state.side}-prev`).onclick = () => { if (state.page > 0) { state.page -= 1; render(state); } };
  document.getElementById(`${state.side}-next`).onclick = () => { if (state.page + 1 < state.total) { state.page += 1; render(state); } };
  document.getElementById(`${state.side}-zoom-out`).onclick = () => { state.zoom = Math.max(.4, state.zoom - .1); render(state); };
  document.getElementById(`${state.side}-zoom-in`).onclick = () => { state.zoom = Math.min(2.5, state.zoom + .1); render(state); };
}

bind(leftState); bind(rightState);
window.loadPair = async (payload) => {
  await wasmReady;
  await Promise.all([
    loadOne(leftState, payload.left_base64, payload.left_name),
    loadOne(rightState, payload.right_base64, payload.right_name),
  ]);
  window.previewResult = { leftPages: leftState.total, rightPages: rightState.total };
  return window.previewResult;
};
window.addEventListener('beforeunload', () => {
  if (leftState.doc) leftState.doc.free();
  if (rightState.doc) rightState.doc.free();
});
