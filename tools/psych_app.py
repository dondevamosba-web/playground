from flask import Flask, request, jsonify
import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, 'token_sheets.json')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
SHEET_NAME = 'Ejercicios Psicología'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ejercicios</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #F5F0EB;
      color: #2C3340;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .screen { display: none; width: 100%; max-width: 480px; padding: 24px 20px; }
    .screen.active { display: flex; flex-direction: column; min-height: 100vh; overflow-y: auto; }

    h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 8px; }
    h2 { font-size: 1.25rem; font-weight: 600; margin-bottom: 6px; }
    .subtitle { color: #6B7280; font-size: 0.9rem; margin-bottom: 32px; }

    .btn {
      display: block;
      width: 100%;
      padding: 18px 20px;
      border: none;
      border-radius: 14px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      text-align: left;
      margin-bottom: 12px;
      transition: opacity 0.15s;
    }
    .btn:active { opacity: 0.8; }

    .btn-registro    { background: #C8DDE2; color: #1A3A42; }
    .btn-relato      { background: #C8D9C4; color: #1A3A2A; }
    .btn-pensamiento { background: #DDD5F0; color: #2A1A42; }
    .btn-primary  { background: #4A7C87; color: #fff; text-align: center; margin-top: auto; padding: 16px; border-radius: 12px; }
    .btn-back     { background: none; border: none; color: #6B7280; cursor: pointer; font-size: 0.9rem; padding: 0; margin-bottom: 24px; width: auto; display: inline-block; }

    .btn-emoji { font-size: 1.5rem; display: block; margin-bottom: 6px; }
    .btn-label { font-size: 1rem; font-weight: 600; }
    .btn-desc  { font-size: 0.8rem; opacity: 0.7; margin-top: 2px; }

    /* Step form */
    .progress-bar { height: 4px; background: #DDD; border-radius: 2px; margin-bottom: 32px; }
    .progress-fill { height: 100%; background: #4A7C87; border-radius: 2px; transition: width 0.3s; }

    .step { display: none; flex-direction: column; flex: 1; }
    .step.active { display: flex; }

    label { font-size: 0.8rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; display: block; }
    .question { font-size: 1.15rem; font-weight: 500; margin-bottom: 6px; line-height: 1.4; }
    .hint { font-size: 0.85rem; color: #9CA3AF; margin-bottom: 20px; }

    textarea, input[type="text"] {
      width: 100%;
      border: 2px solid #E5E0D8;
      border-radius: 10px;
      padding: 14px;
      font-size: 1rem;
      font-family: inherit;
      background: #FEFCF8;
      resize: none;
      outline: none;
      transition: border-color 0.2s;
      color: #2C3340;
    }
    textarea:focus, input[type="text"]:focus { border-color: #4A7C87; }
    textarea { min-height: 120px; }

    .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .chip {
      padding: 8px 14px;
      border: 2px solid #E5E0D8;
      border-radius: 20px;
      font-size: 0.85rem;
      cursor: pointer;
      background: #FEFCF8;
      transition: all 0.15s;
      color: #2C3340;
    }
    .chip.selected { background: #4A7C87; border-color: #4A7C87; color: #fff; }

    /* Relato */
    .relato-field { margin-bottom: 20px; }

    /* Success */
    .success-icon { font-size: 3rem; text-align: center; margin-bottom: 16px; }
    .success-msg { text-align: center; color: #4A7C87; font-size: 1.1rem; margin-bottom: 8px; font-weight: 500; }
    .success-sub { text-align: center; color: #9CA3AF; font-size: 0.9rem; margin-bottom: 40px; }

    .spacer { flex: 1; }
    .nav-row { display: flex; gap: 10px; margin-top: 20px; }
    .nav-row .btn-primary { flex: 1; margin-top: 0; }
    .btn-skip { background: none; border: 2px solid #E5E0D8; color: #9CA3AF; text-align: center; border-radius: 12px; padding: 14px; flex: 0 0 auto; font-size: 0.85rem; cursor: pointer; }

    .error-msg { color: #E05252; font-size: 0.85rem; margin-top: 8px; display: none; }

    .adela {
      position: fixed;
      bottom: 12px;
      right: 16px;
      font-size: 0.65rem;
      letter-spacing: 0.12em;
      color: #C8BFB5;
      text-transform: uppercase;
      pointer-events: none;
      user-select: none;
    }
  </style>
</head>
<body>

<span class="adela">adela suelta</span>

<!-- HOME -->
<div id="home" class="screen active">
  <div style="flex:1; display:flex; flex-direction:column; justify-content:center; padding: 16px 0;">
    <h1>Hola 👋</h1>
    <p class="subtitle">¿Qué ejercicio querés hacer?</p>
    <button class="btn btn-registro" onclick="show('registro')">
      <span class="btn-emoji">🧠</span>
      <span class="btn-label">Registrar síntoma</span>
      <span class="btn-desc">Cuando aparece algo</span>
    </button>
    <button class="btn btn-relato" onclick="show('relato')">
      <span class="btn-emoji">📝</span>
      <span class="btn-label">Relato del día</span>
      <span class="btn-desc">Una vez por día</span>
    </button>
    <button class="btn btn-pensamiento" onclick="show('pensamiento')">
      <span class="btn-emoji">🌀</span>
      <span class="btn-label">Pensamiento automático</span>
      <span class="btn-desc">Cuando aparece un pensamiento negativo</span>
    </button>
  </div>
</div>

<!-- REGISTRO (step by step) -->
<div id="registro" class="screen">
  <button class="btn-back" onclick="show('home')">← Volver</button>
  <div class="progress-bar"><div class="progress-fill" id="reg-progress" style="width:14%"></div></div>

  <!-- Step 1 -->
  <div class="step active" id="reg-step-1">
    <label>Paso 1 de 7</label>
    <p class="question">¿Qué hora era y dónde estabas?</p>
    <textarea id="r-hora_lugar" placeholder="Ej: 14:30, en la oficina..." rows="3"></textarea>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-primary" onclick="regNext(1)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 2 -->
  <div class="step" id="reg-step-2">
    <label>Paso 2 de 7</label>
    <p class="question">¿En qué parte del cuerpo lo sentiste?</p>
    <input type="text" id="r-parte_cuerpo" placeholder="Ej: pecho, cabeza, estómago..." />
    <div class="chips" id="body-chips">
      <span class="chip" onclick="chipSelect(this, 'r-parte_cuerpo')">Pecho</span>
      <span class="chip" onclick="chipSelect(this, 'r-parte_cuerpo')">Cabeza</span>
      <span class="chip" onclick="chipSelect(this, 'r-parte_cuerpo')">Estómago</span>
      <span class="chip" onclick="chipSelect(this, 'r-parte_cuerpo')">Garganta</span>
      <span class="chip" onclick="chipSelect(this, 'r-parte_cuerpo')">Espalda</span>
      <span class="chip" onclick="chipSelect(this, 'r-parte_cuerpo')">Piernas</span>
    </div>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="regPrev(2)">←</button>
      <button class="btn-primary" onclick="regNext(2)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 3 -->
  <div class="step" id="reg-step-3">
    <label>Paso 3 de 7</label>
    <p class="question">¿Cómo lo describís?</p>
    <input type="text" id="r-descripcion" placeholder="Ej: punzante, presión..." />
    <div class="chips">
      <span class="chip" onclick="chipSelect(this, 'r-descripcion')">Punzante</span>
      <span class="chip" onclick="chipSelect(this, 'r-descripcion')">Tirante</span>
      <span class="chip" onclick="chipSelect(this, 'r-descripcion')">Presión</span>
      <span class="chip" onclick="chipSelect(this, 'r-descripcion')">Quemazón</span>
      <span class="chip" onclick="chipSelect(this, 'r-descripcion')">Latidos</span>
      <span class="chip" onclick="chipSelect(this, 'r-descripcion')">Adormecido</span>
    </div>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="regPrev(3)">←</button>
      <button class="btn-primary" onclick="regNext(3)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 4 -->
  <div class="step" id="reg-step-4">
    <label>Paso 4 de 7</label>
    <p class="question">¿Qué actividad estabas haciendo en ese momento?</p>
    <textarea id="r-actividad" placeholder="Ej: trabajando en la computadora, caminando..." rows="3"></textarea>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="regPrev(4)">←</button>
      <button class="btn-primary" onclick="regNext(4)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 5 -->
  <div class="step" id="reg-step-5">
    <label>Paso 5 de 7</label>
    <p class="question">¿Cómo venía el día hasta ahí?</p>
    <p class="hint">¿Pasó algo destacable antes?</p>
    <textarea id="r-horas_previas" placeholder="Ej: tuve una reunión tensa, dormí poco..." rows="4"></textarea>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="regPrev(5)">←</button>
      <button class="btn-primary" onclick="regNext(5)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 6 -->
  <div class="step" id="reg-step-6">
    <label>Paso 6 de 7</label>
    <p class="question">¿Cómo te sentías justo antes?</p>
    <p class="hint">1 o 2 palabras alcanza</p>
    <input type="text" id="r-estado_emocional" placeholder="Ej: ansioso, tranquilo, cansado..." />
    <div class="chips">
      <span class="chip" onclick="chipSelect(this, 'r-estado_emocional')">Ansioso</span>
      <span class="chip" onclick="chipSelect(this, 'r-estado_emocional')">Cansado</span>
      <span class="chip" onclick="chipSelect(this, 'r-estado_emocional')">Tranquilo</span>
      <span class="chip" onclick="chipSelect(this, 'r-estado_emocional')">Estresado</span>
      <span class="chip" onclick="chipSelect(this, 'r-estado_emocional')">Concentrado</span>
      <span class="chip" onclick="chipSelect(this, 'r-estado_emocional')">Disperso</span>
    </div>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="regPrev(6)">←</button>
      <button class="btn-primary" onclick="regNext(6)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 7 -->
  <div class="step" id="reg-step-7">
    <label>Paso 7 de 7</label>
    <p class="question">¿Cómo reaccionaste? ¿Qué pasó después?</p>
    <textarea id="r-reaccion" placeholder="Ej: lo ignoré, paré lo que hacía, googleé..." rows="3"></textarea>
    <textarea id="r-como_siguio" placeholder="¿Cómo siguió después? (se fue, bajó, empeoró...)" rows="3" style="margin-top:12px"></textarea>
    <p id="reg-error" class="error-msg">Hubo un error al guardar. Intentá de nuevo.</p>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="regPrev(7)">←</button>
      <button class="btn-primary" id="reg-submit-btn" onclick="submitRegistro()">Guardar ✓</button>
    </div>
  </div>
</div>

<!-- RELATO DEL DÍA -->
<div id="relato" class="screen">
  <button class="btn-back" onclick="show('home')">← Volver</button>
  <h2>📝 Relato del día</h2>
  <p class="subtitle">Sin analizar, sin explicar por qué. Solo describir.</p>

  <div class="relato-field">
    <label>¿Qué hiciste?</label>
    <textarea id="rel-que_hiciste" placeholder="Contame qué hiciste hoy..." rows="4"></textarea>
  </div>
  <div class="relato-field">
    <label>¿Cómo te sentiste en general?</label>
    <textarea id="rel-como_te_sentiste" placeholder="Cómo estuvo tu estado de ánimo..." rows="4"></textarea>
  </div>
  <div class="relato-field">
    <label>¿Cómo estuvo tu cuerpo?</label>
    <textarea id="rel-como_estuvo_cuerpo" placeholder="Qué sentiste físicamente..." rows="4"></textarea>
  </div>

  <p id="rel-error" class="error-msg">Hubo un error al guardar. Intentá de nuevo.</p>
  <button class="btn-primary" id="rel-submit-btn" onclick="submitRelato()">Guardar ✓</button>
</div>

<!-- PENSAMIENTO AUTOMÁTICO (TCC) -->
<div id="pensamiento" class="screen">
  <button class="btn-back" onclick="show('home')">← Volver</button>
  <div class="progress-bar"><div class="progress-fill" id="pen-progress" style="width:14%"></div></div>

  <!-- Step 1 -->
  <div class="step active" id="pen-step-1">
    <label>Paso 1 de 7</label>
    <p class="question">¿Qué estaba pasando cuando apareció el pensamiento?</p>
    <p class="hint">Situación, hora, lugar, con quién estabas</p>
    <textarea id="p-situacion" placeholder="Ej: Estaba en el trabajo después de mandar un mail equivocado..." rows="4"></textarea>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-primary" onclick="penNext(1)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 2 -->
  <div class="step" id="pen-step-2">
    <label>Paso 2 de 7</label>
    <p class="question">¿Qué pensaste exactamente?</p>
    <p class="hint">El pensamiento tal como apareció, sin filtro</p>
    <textarea id="p-pensamiento" placeholder="Ej: Me van a echar del trabajo. No sirvo para esto..." rows="4"></textarea>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="penPrev(2)">←</button>
      <button class="btn-primary" onclick="penNext(2)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 3 -->
  <div class="step" id="pen-step-3">
    <label>Paso 3 de 7</label>
    <p class="question">¿Qué emoción sentiste? ¿Qué tan intensa fue del 1 al 10?</p>
    <input type="text" id="p-emocion" placeholder="Ej: Miedo — 8/10" />
    <div class="chips">
      <span class="chip" onclick="chipSelect(this, 'p-emocion')">Miedo</span>
      <span class="chip" onclick="chipSelect(this, 'p-emocion')">Vergüenza</span>
      <span class="chip" onclick="chipSelect(this, 'p-emocion')">Angustia</span>
      <span class="chip" onclick="chipSelect(this, 'p-emocion')">Enojo</span>
      <span class="chip" onclick="chipSelect(this, 'p-emocion')">Tristeza</span>
      <span class="chip" onclick="chipSelect(this, 'p-emocion')">Ansiedad</span>
    </div>
    <input type="text" id="p-intensidad" placeholder="Intensidad del 1 al 10" style="margin-top:12px" />
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="penPrev(3)">←</button>
      <button class="btn-primary" onclick="penNext(3)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 4 -->
  <div class="step" id="pen-step-4">
    <label>Paso 4 de 7</label>
    <p class="question">¿Qué pruebas tenés a favor de ese pensamiento?</p>
    <p class="hint">Hechos concretos, no interpretaciones</p>
    <textarea id="p-a_favor" placeholder="Ej: Me equivoqué en el mail. Mi jefe no respondió todavía..." rows="4"></textarea>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="penPrev(4)">←</button>
      <button class="btn-primary" onclick="penNext(4)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 5 -->
  <div class="step" id="pen-step-5">
    <label>Paso 5 de 7</label>
    <p class="question">¿Qué pruebas tenés en contra?</p>
    <p class="hint">¿Qué datos contradicen o relativizan ese pensamiento?</p>
    <textarea id="p-en_contra" placeholder="Ej: Nunca me llamaron la atención antes. Todos cometemos errores. Mi jefe valora mi trabajo..." rows="4"></textarea>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="penPrev(5)">←</button>
      <button class="btn-primary" onclick="penNext(5)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 6 -->
  <div class="step" id="pen-step-6">
    <label>Paso 6 de 7</label>
    <p class="question">¿Reconocés alguna de estas trampas del pensamiento?</p>
    <p class="hint">Podés elegir más de una</p>
    <input type="text" id="p-distorsion" placeholder="Seleccioná o escribí..." />
    <div class="chips" id="distorsion-chips">
      <span class="chip" onclick="chipMulti(this, 'p-distorsion')">Catastrofizar</span>
      <span class="chip" onclick="chipMulti(this, 'p-distorsion')">Todo o nada</span>
      <span class="chip" onclick="chipMulti(this, 'p-distorsion')">Leer la mente</span>
      <span class="chip" onclick="chipMulti(this, 'p-distorsion')">Filtro negativo</span>
      <span class="chip" onclick="chipMulti(this, 'p-distorsion')">Sacar conclusiones</span>
      <span class="chip" onclick="chipMulti(this, 'p-distorsion')">Personalizar</span>
    </div>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="penPrev(6)">←</button>
      <button class="btn-primary" onclick="penNext(6)">Siguiente →</button>
    </div>
  </div>

  <!-- Step 7 -->
  <div class="step" id="pen-step-7">
    <label>Paso 7 de 7</label>
    <p class="question">¿Qué le dirías a un amigo que tuviera este pensamiento?</p>
    <p class="hint">Escribí una versión más equilibrada y realista del pensamiento</p>
    <textarea id="p-alternativo" placeholder="Ej: Me equivoqué en algo puntual. No significa que me vayan a echar. Puedo aclararlo mañana..." rows="4"></textarea>
    <p id="pen-error" class="error-msg">Hubo un error al guardar. Intentá de nuevo.</p>
    <div class="spacer"></div>
    <div class="nav-row">
      <button class="btn-skip" onclick="penPrev(7)">←</button>
      <button class="btn-primary" id="pen-submit-btn" onclick="submitPensamiento()">Guardar ✓</button>
    </div>
  </div>
</div>

<!-- SUCCESS -->
<div id="success" class="screen">
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
    <div class="success-icon">✅</div>
    <p class="success-msg">Guardado</p>
    <p class="success-sub">Ya quedó registrado.</p>
    <div style="background:#EAF0F2;border-radius:14px;padding:20px 18px;margin:24px 0 32px;">
      <p id="quote-text" style="font-size:1rem;line-height:1.6;color:#4A7C87;font-style:italic;text-align:center;"></p>
    </div>
    <button class="btn btn-registro" onclick="show('home')" style="text-align:center;">Volver al inicio</button>
  </div>
</div>

<script>
  function show(screen) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screen).classList.add('active');
    if (screen === 'registro') resetRegistro();
    if (screen === 'pensamiento') resetPensamiento();
  }

  function resetRegistro() {
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    document.getElementById('reg-step-1').classList.add('active');
    document.getElementById('reg-progress').style.width = '14%';
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
    ['r-hora_lugar','r-parte_cuerpo','r-descripcion','r-actividad','r-horas_previas','r-estado_emocional','r-reaccion','r-como_siguio'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
  }

  function chipSelect(chip, fieldId) {
    const field = document.getElementById(fieldId);
    chip.closest('.chips').querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
    chip.classList.add('selected');
    field.value = chip.textContent;
  }

  function chipMulti(chip, fieldId) {
    chip.classList.toggle('selected');
    const selected = chip.closest('.chips').querySelectorAll('.chip.selected');
    document.getElementById(fieldId).value = Array.from(selected).map(c => c.textContent).join(', ');
  }

  function regNext(step) {
    document.getElementById('reg-step-' + step).classList.remove('active');
    const next = step + 1;
    document.getElementById('reg-step-' + next).classList.add('active');
    document.getElementById('reg-progress').style.width = (next / 7 * 100) + '%';
  }

  function regPrev(step) {
    document.getElementById('reg-step-' + step).classList.remove('active');
    const prev = step - 1;
    document.getElementById('reg-step-' + prev).classList.add('active');
    document.getElementById('reg-progress').style.width = (prev / 7 * 100) + '%';
  }

  async function submitRegistro() {
    const btn = document.getElementById('reg-submit-btn');
    btn.textContent = 'Guardando...';
    btn.disabled = true;
    const payload = {
      hora_lugar:      document.getElementById('r-hora_lugar').value,
      parte_cuerpo:    document.getElementById('r-parte_cuerpo').value,
      descripcion:     document.getElementById('r-descripcion').value,
      actividad:       document.getElementById('r-actividad').value,
      horas_previas:   document.getElementById('r-horas_previas').value,
      estado_emocional:document.getElementById('r-estado_emocional').value,
      reaccion:        document.getElementById('r-reaccion').value,
      como_siguio:     document.getElementById('r-como_siguio').value,
    };
    try {
      const res = await fetch('/api/registro', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      if (!res.ok) throw new Error();
      showQuote(); show('success');
    } catch {
      document.getElementById('reg-error').style.display = 'block';
    } finally {
      btn.textContent = 'Guardar ✓';
      btn.disabled = false;
    }
  }

  const QUOTES = [
    "Notar sin juzgar ya es un acto de valentía.",
    "El cuerpo habla. Vos lo estás escuchando.",
    "Registrar es cuidarse.",
    "No tenés que resolver nada ahora. Solo observar.",
    "Cada registro es un paso hacia entenderte mejor.",
    "Lo que nombramos pierde un poco de su poder.",
    "Estar presente con lo que hay es suficiente.",
    "Ya hiciste lo más difícil: pararte y mirar.",
  ];

  function showQuote() {
    const q = QUOTES[Math.floor(Math.random() * QUOTES.length)];
    document.getElementById('quote-text').textContent = '"' + q + '"';
  }

  function resetPensamiento() {
    document.querySelectorAll('#pensamiento .step').forEach(s => s.classList.remove('active'));
    document.getElementById('pen-step-1').classList.add('active');
    document.getElementById('pen-progress').style.width = '14%';
    document.querySelectorAll('#pensamiento .chip').forEach(c => c.classList.remove('selected'));
    ['p-situacion','p-pensamiento','p-emocion','p-intensidad','p-a_favor','p-en_contra','p-distorsion','p-alternativo'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
  }

  function penNext(step) {
    document.getElementById('pen-step-' + step).classList.remove('active');
    const next = step + 1;
    document.getElementById('pen-step-' + next).classList.add('active');
    document.getElementById('pen-progress').style.width = (next / 7 * 100) + '%';
  }

  function penPrev(step) {
    document.getElementById('pen-step-' + step).classList.remove('active');
    const prev = step - 1;
    document.getElementById('pen-step-' + prev).classList.add('active');
    document.getElementById('pen-progress').style.width = (prev / 7 * 100) + '%';
  }

  async function submitPensamiento() {
    const btn = document.getElementById('pen-submit-btn');
    btn.textContent = 'Guardando...';
    btn.disabled = true;
    const payload = {
      situacion:   document.getElementById('p-situacion').value,
      pensamiento: document.getElementById('p-pensamiento').value,
      emocion:     document.getElementById('p-emocion').value,
      intensidad:  document.getElementById('p-intensidad').value,
      a_favor:     document.getElementById('p-a_favor').value,
      en_contra:   document.getElementById('p-en_contra').value,
      distorsion:  document.getElementById('p-distorsion').value,
      alternativo: document.getElementById('p-alternativo').value,
    };
    try {
      const res = await fetch('/api/pensamiento', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      if (!res.ok) throw new Error();
      showQuote(); show('success');
    } catch {
      document.getElementById('pen-error').style.display = 'block';
    } finally {
      btn.textContent = 'Guardar ✓';
      btn.disabled = false;
    }
  }

  document.addEventListener('keydown', function(e) {
    if (e.key !== 'Enter' || e.shiftKey) return;
    const activeScreen = document.querySelector('.screen.active');
    if (!activeScreen) return;
    const screenId = activeScreen.id;
    if (screenId === 'registro') {
      const activeStep = activeScreen.querySelector('.step.active');
      if (!activeStep) return;
      const stepNum = parseInt(activeStep.id.replace('reg-step-', ''));
      e.preventDefault();
      if (stepNum < 7) regNext(stepNum); else submitRegistro();
    } else if (screenId === 'pensamiento') {
      const activeStep = activeScreen.querySelector('.step.active');
      if (!activeStep) return;
      const stepNum = parseInt(activeStep.id.replace('pen-step-', ''));
      e.preventDefault();
      if (stepNum < 7) penNext(stepNum); else submitPensamiento();
    }
  });

  async function submitRelato() {
    const btn = document.getElementById('rel-submit-btn');
    btn.textContent = 'Guardando...';
    btn.disabled = true;
    const payload = {
      que_hiciste:       document.getElementById('rel-que_hiciste').value,
      como_te_sentiste:  document.getElementById('rel-como_te_sentiste').value,
      como_estuvo_cuerpo:document.getElementById('rel-como_estuvo_cuerpo').value,
    };
    try {
      const res = await fetch('/api/relato', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      if (!res.ok) throw new Error();
      showQuote(); show('success');
    } catch {
      document.getElementById('rel-error').style.display = 'block';
    } finally {
      btn.textContent = 'Guardar ✓';
      btn.disabled = false;
    }
  }
</script>
</body>
</html>"""


def get_sheets_client():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return gspread.authorize(creds)


def get_or_create_spreadsheet():
    client = get_sheets_client()
    try:
        ss = client.open(SHEET_NAME)
    except gspread.SpreadsheetNotFound:
        ss = client.create(SHEET_NAME)

    existing_titles = [ws.title for ws in ss.worksheets()]

    if 'Registro' not in existing_titles:
        if existing_titles and existing_titles[0] not in ('Registro', 'Relato del día'):
            reg = ss.sheet1
            reg.update_title('Registro')
        else:
            reg = ss.add_worksheet('Registro', rows=1000, cols=10)
        reg.append_row(['Timestamp', 'Hora y lugar', 'Parte del cuerpo', 'Descripción', 'Actividad', 'Horas previas', 'Estado emocional', 'Reacción', 'Cómo siguió'])

    if 'Relato del día' not in existing_titles:
        relato = ss.add_worksheet('Relato del día', rows=1000, cols=5)
        relato.append_row(['Timestamp', 'Qué hiciste', 'Cómo te sentiste', 'Cómo estuvo el cuerpo'])

    if 'Pensamientos' not in existing_titles:
        pen = ss.add_worksheet('Pensamientos', rows=1000, cols=10)
        pen.append_row(['Timestamp', 'Situación', 'Pensamiento automático', 'Emoción', 'Intensidad', 'Pruebas a favor', 'Pruebas en contra', 'Distorsión', 'Pensamiento alternativo'])

    return ss


@app.route('/')
def index():
    return HTML


@app.route('/api/registro', methods=['POST'])
def save_registro():
    data = request.json
    ws = get_or_create_spreadsheet().worksheet('Registro')
    ws.append_row([
        datetime.now().strftime('%Y-%m-%d %H:%M'),
        data.get('hora_lugar', ''),
        data.get('parte_cuerpo', ''),
        data.get('descripcion', ''),
        data.get('actividad', ''),
        data.get('horas_previas', ''),
        data.get('estado_emocional', ''),
        data.get('reaccion', ''),
        data.get('como_siguio', ''),
    ])
    return jsonify({'ok': True})


@app.route('/api/pensamiento', methods=['POST'])
def save_pensamiento():
    data = request.json
    ws = get_or_create_spreadsheet().worksheet('Pensamientos')
    ws.append_row([
        datetime.now().strftime('%Y-%m-%d %H:%M'),
        data.get('situacion', ''),
        data.get('pensamiento', ''),
        data.get('emocion', ''),
        data.get('intensidad', ''),
        data.get('a_favor', ''),
        data.get('en_contra', ''),
        data.get('distorsion', ''),
        data.get('alternativo', ''),
    ])
    return jsonify({'ok': True})


@app.route('/api/relato', methods=['POST'])
def save_relato():
    data = request.json
    ws = get_or_create_spreadsheet().worksheet('Relato del día')
    ws.append_row([
        datetime.now().strftime('%Y-%m-%d %H:%M'),
        data.get('que_hiciste', ''),
        data.get('como_te_sentiste', ''),
        data.get('como_estuvo_cuerpo', ''),
    ])
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5050)
