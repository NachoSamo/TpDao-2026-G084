// Agrega un botón "Exportar JPG" que descarga el diagrama de la página en alta resolución.
// Sin librerías: clona el diagrama, lo envuelve en un SVG (foreignObject) con los estilos de la
// página en tema claro y lo rasteriza en un <canvas>. Funciona abriendo el .html directo en Chrome/Edge.
(() => {
  const ESCALA = 3, CALIDAD = 0.95, FONDO = '#ffffff';

  // Arma fuera de pantalla una copia del título, la leyenda y el diagrama, a tamaño real (zoom 100 %).
  function armarCopia() {
    const cont = document.createElement('div');
    cont.style.cssText = `--bg:${FONDO};background:${FONDO};color:var(--ink);font:14px/1.4 system-ui,sans-serif;`
      + 'padding:20px;display:inline-block;position:absolute;left:-100000px;top:0;';

    const lienzo = document.getElementById('canvas');
    if (lienzo) { // diagrama de clases y DER: cajas HTML + SVG de relaciones
      const cab = document.createElement('header');
      cab.className = 'top';
      cab.style.cssText = 'position:static;padding:0 0 12px;margin-bottom:12px;background:none;';
      cab.append(document.querySelector('header.top h1').cloneNode(true), document.querySelector('header.top .legend').cloneNode(true));
      cab.querySelectorAll('.legend span').forEach(s => { s.innerHTML = s.innerHTML.replace(/\s*·\s*pasá el mouse.*$/, ''); });
      const copia = lienzo.cloneNode(true);
      copia.removeAttribute('id');
      copia.classList.remove('focusing');
      copia.style.cssText += ';position:relative;transform:none;';
      copia.querySelectorAll('.on, .focus').forEach(e => e.classList.remove('on', 'focus'));
      cont.append(cab, copia);
    } else { // máquina de estados: SVG estático
      const svg = document.querySelector('.diagram svg').cloneNode(true);
      const [, , w, h] = svg.getAttribute('viewBox').split(/\s+/).map(Number);
      svg.setAttribute('width', w); svg.setAttribute('height', h);
      svg.style.cssText = 'display:block;min-width:0;';
      const diag = document.createElement('div');
      diag.className = 'diagram';
      diag.style.cssText = 'overflow:visible;';
      diag.append(svg);
      cont.append(document.querySelector('main h1').cloneNode(true), document.querySelector('main p.sub').cloneNode(true), diag);
    }
    document.body.append(cont);
    return cont;
  }

  async function generarJPG() {
    const cont = armarCopia();
    try {
      const w = Math.ceil(cont.scrollWidth), h = Math.ceil(cont.scrollHeight);
      const salida = cont.cloneNode(true);
      salida.style.position = salida.style.left = salida.style.top = '';
      const css = [...document.querySelectorAll('style')].map(s => s.textContent).join('\n');
      const html = new XMLSerializer().serializeToString(salida);
      // data-theme="light" en la raíz fuerza la paleta clara aunque el sistema esté en modo oscuro
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" data-theme="light" width="${w}" height="${h}">`
        + `<style><![CDATA[${css.replace(/]]>/g, '')}]]></style><foreignObject x="0" y="0" width="${w}" height="${h}">${html}</foreignObject></svg>`;
      const img = new Image();
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
      await img.decode();
      const c = document.createElement('canvas');
      c.width = w * ESCALA; c.height = h * ESCALA;
      const ctx = c.getContext('2d');
      ctx.fillStyle = FONDO; ctx.fillRect(0, 0, c.width, c.height);
      ctx.drawImage(img, 0, 0, c.width, c.height);
      return await new Promise((ok, mal) => c.toBlob(b => b ? ok(b) : mal(new Error('toBlob vacío')), 'image/jpeg', CALIDAD));
    } finally {
      cont.remove();
    }
  }

  async function exportar(boton) {
    const texto = boton.textContent;
    boton.disabled = true; boton.textContent = 'Generando…';
    try {
      const blob = await generarJPG();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = (location.pathname.split('/').pop() || 'diagrama').replace(/\.html?$/i, '') + '.jpg';
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 10000);
    } catch (e) {
      console.error(e);
      alert('No se pudo exportar la imagen en este navegador. Probá abriendo el archivo con Chrome o Edge.');
    } finally {
      boton.disabled = false; boton.textContent = texto;
    }
  }

  const boton = document.createElement('button');
  boton.type = 'button';
  boton.textContent = 'Exportar JPG';
  boton.title = `Descarga el diagrama en alta resolución (×${ESCALA}, fondo blanco)`;
  boton.style.cssText = 'font:600 12px system-ui,sans-serif;padding:5px 12px;border-radius:4px;cursor:pointer;'
    + 'border:1px solid var(--line);background:var(--box);color:var(--ink);';
  boton.addEventListener('click', () => exportar(boton));
  const zoom = document.querySelector('header.top .zoom');
  if (zoom) zoom.after(boton); else document.querySelector('main h1').after(boton);

  window.generarJPG = generarJPG; // para probar desde la consola
})();
