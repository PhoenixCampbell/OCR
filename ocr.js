const ocrDemo = (() => {
  let canvas, ctx, drawing = false, last = null;

  function onLoadFunction() {
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    ctx.lineWidth = 16;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.fillStyle = 'white';
    ctx.strokeStyle = 'black';

    // white background so downscaling works
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // mouse
    canvas.addEventListener('mousedown', e => { drawing = true; last = pos(e); });
    window.addEventListener('mouseup', () => drawing = false);
    canvas.addEventListener('mousemove', e => drawTo(e));

    // touch
    canvas.addEventListener('touchstart', e => { e.preventDefault(); drawing = true; last = pos(e.touches[0]); });
    canvas.addEventListener('touchend', () => drawing = false);
    canvas.addEventListener('touchmove', e => { e.preventDefault(); drawTo(e.touches[0]); });

    // expose API to buttons
    window.ocrDemo = { onLoadFunction, train, test, resetCanvas };
  }

  function pos(e) {
    const r = canvas.getBoundingClientRect();
    return { x: (e.clientX - r.left) * (canvas.width / r.width),
             y: (e.clientY - r.top) * (canvas.height / r.height) };
  }

  function drawTo(e) {
    if (!drawing) return;
    const p = pos(e);
    ctx.beginPath();
    ctx.moveTo(last.x, last.y);
    ctx.lineTo(p.x, p.y);
    ctx.stroke();
    last = p;
  }

  function resetCanvas() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'white';
  }

  // Downscale to 20x20 grayscale [0,1] (black ink ~1)
  function get20x20() {
    const tmp = document.createElement('canvas');
    tmp.width = 20; tmp.height = 20;
    const tctx = tmp.getContext('2d');

    // draw with high-quality sampling
    tctx.fillStyle = 'white'; tctx.fillRect(0, 0, 20, 20);
    tctx.drawImage(canvas, 0, 0, 20, 20);

    const { data } = tctx.getImageData(0, 0, 20, 20);
    const out = [];
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i], g = data[i+1], b = data[i+2];
      // grayscale and invert so black strokes ≈ 1.0
      const gray = (0.299*r + 0.587*g + 0.114*b) / 255;
      out.push(1 - gray);
    }
    return out; // length 400
  }

  async function train() {
    const label = document.getElementById('digit').value.trim();
    if (!/^\d$/.test(label)) { alert('Enter a single digit (0–9)'); return; }
    const pixels = get20x20();
    await fetch('/ocr', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ train: true, trainArray: [{ y0: pixels, label: Number(label) }] })
    });
    alert('Trained 1 sample');
  }

async function test() {
  const API = 'http://127.0.0.1:8000/ocr';
  const pixels = get20x20();
  const res = await fetch(API, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ predict:true, image:pixels })
});

  let text = await res.text();      // read as text first for debugging
  try {
       const json = JSON.parse(text);
       if (!res.ok || json.ok === false) {
         alert('Server error:\n' + (json.error || res.status + ' ' + res.statusText));
         console.error(json.trace || '');
         return;
       }
       alert('Prediction: ' + json.result);
  } catch (e) {
       console.error('Non-JSON response:', text);
       alert('Bad response from server (see console)');
  }
}
  return { onLoadFunction, train, test, resetCanvas };
})();
