#!/bin/zsh
cd "${0:A:h}"
if command -v python3 >/dev/null; then
  TP_PYTHON=python3
else
  echo 'Instalá Python 3.12 o superior para ejecutar el TP.'
  read '?Presioná Enter para cerrar.'
  exit 1
fi
if [[ ! -f demo-anden.db ]]; then
  "$TP_PYTHON" -m distribucion.demo_web --db demo-anden.db || exit 1
fi
echo 'Abrí http://127.0.0.1:8080 en tu navegador. Ctrl+C detiene el servidor.'
"$TP_PYTHON" main.py --web --db demo-anden.db --port 8080
if [[ $? -ne 0 ]]; then
  echo 'Si el puerto ya está en uso, abrí http://127.0.0.1:8080 o usá --port 8081.'
  read '?Presioná Enter para cerrar.'
fi
