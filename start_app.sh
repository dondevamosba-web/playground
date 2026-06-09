#!/bin/bash
cd "$(dirname "$0")"

python3 tools/psych_app.py &
FLASK_PID=$!

sleep 2

ngrok http 5050 &
NGROK_PID=$!

echo ""
echo "App running at: https://ducktail-morbidity-dimly.ngrok-free.dev"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $FLASK_PID $NGROK_PID 2>/dev/null" EXIT
wait
