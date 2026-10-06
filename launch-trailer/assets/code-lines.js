/* Gerado por scripts/extract-code.mjs a partir de index.html. Não editar. */
window.CODE_LINES = [
  "const hook = \"Nada aqui foi filmado.\";",
  "const T = window.FILM_T;",
  "    ctx.lineTo(x, waveY + v + 1.5);",
  "  const tl = gsap.timeline({ paused: true });",
  "  const pull = { x: camX, y: camY, scale: camS, duration: 1.05 };",
  "  tl.fromTo(cam, { x: 0, y: 0, scale: 1 }, { ...pull, ease: \"expo.inOut\" }, T.pullBack);",
  "  const focus = { filter: \"blur(10px)\", opacity: 0.3, duration: 0.9 };",
  "  tl.fromTo(camWrap, { filter: \"blur(0px)\" }, { ...focus, ease: \"power2.inOut\" }, T.focus);",
  "  tl.to(pt, { x: dp.cx, y: dp.b, duration: 0.45, ease: \"back.in(1.6)\" }, 11.45);",
  "  const flood = { duration: 0.9, ease: \"expo.out\" };",
  "  tl.fromTo(cream, { clipPath: circle(0) }, { clipPath: circle(R), ...flood }, T.impact);",
  "  window.__timelines[\"main\"] = tl;"
];
