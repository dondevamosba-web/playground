const SKIN = '#f2dfc8';
const SKIN_STROKE = '#c4956a';
const SKIN_DARK = '#e8c9a8';

export default function BodyMapFront({ getStyle, onSelect }) {
  const ms = getStyle;

  return (
    <svg viewBox="0 0 240 560" xmlns="http://www.w3.org/2000/svg"
      style={{ width: '100%', height: '100%', maxHeight: '100%' }}>
      <defs>
        <radialGradient id="skinGrad" cx="50%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#f7e8d5" />
          <stop offset="100%" stopColor="#e0b88a" />
        </radialGradient>
        <filter id="softShadow" x="-10%" y="-10%" width="120%" height="120%">
          <feDropShadow dx="1" dy="2" stdDeviation="2" floodOpacity="0.12" />
        </filter>
      </defs>

      {/* ── BODY OUTLINE (skin) ── */}

      {/* Head */}
      <ellipse cx="120" cy="36" rx="24" ry="28" fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1.2" />
      {/* Ear left */}
      <ellipse cx="96" cy="38" rx="4" ry="6" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" />
      {/* Ear right */}
      <ellipse cx="144" cy="38" rx="4" ry="6" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" />

      {/* Neck */}
      <path d="M111 62 Q110 72 110 82 L130 82 Q130 72 129 62 Z" fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Main torso */}
      <path d="
        M110 80
        Q85 82 68 92
        Q52 102 50 118
        Q48 138 52 158
        Q56 178 60 202
        Q63 224 64 252
        Q66 268 68 282
        L172 282
        Q174 268 176 252
        Q177 224 180 202
        Q184 178 188 158
        Q192 138 190 118
        Q188 102 172 92
        Q155 82 130 80 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1.2" />

      {/* Left upper arm */}
      <path d="
        M52 112
        Q40 126 36 158
        Q33 182 35 214
        Q36 226 38 238
        L56 236
        Q57 224 58 212
        Q58 182 62 158
        Q66 130 68 114 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Right upper arm */}
      <path d="
        M188 112
        Q200 126 204 158
        Q207 182 205 214
        Q204 226 202 238
        L184 236
        Q183 224 182 212
        Q182 182 178 158
        Q174 130 172 114 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left forearm */}
      <path d="M38 236 Q32 258 32 288 Q32 304 34 316 L54 314 Q55 302 56 288 Q57 258 56 236 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Right forearm */}
      <path d="M202 236 Q208 258 208 288 Q208 304 206 316 L186 314 Q185 302 184 288 Q183 258 184 236 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left hand */}
      <ellipse cx="43" cy="322" rx="10" ry="12" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" />
      {/* Right hand */}
      <ellipse cx="197" cy="322" rx="10" ry="12" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" />

      {/* Hips/pelvis */}
      <path d="M68 280 Q62 300 62 318 L178 318 Q178 300 172 280 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left thigh */}
      <path d="M62 316 Q56 354 55 392 Q54 418 56 440 L88 440 Q90 418 90 392 Q90 354 88 316 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Right thigh */}
      <path d="M178 316 Q184 354 185 392 Q186 418 184 440 L152 440 Q150 418 150 392 Q150 354 152 316 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left knee */}
      <path d="M55 438 Q53 452 55 464 L88 464 Q90 452 90 438 Z"
        fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="1" />
      {/* Right knee */}
      <path d="M185 438 Q187 452 185 464 L152 464 Q150 452 150 438 Z"
        fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left lower leg */}
      <path d="M55 462 Q53 494 54 524 Q55 536 58 542 L84 542 Q86 536 86 524 Q86 494 86 462 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Right lower leg */}
      <path d="M185 462 Q187 494 186 524 Q185 536 182 542 L158 542 Q156 536 156 524 Q154 494 154 462 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left foot */}
      <path d="M54 540 Q50 548 50 554 L82 554 Q84 552 86 542 Z"
        fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.9" />
      {/* Right foot */}
      <path d="M186 540 Q190 548 190 554 L158 554 Q156 552 154 542 Z"
        fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.9" />

      {/* ── MUSCLE REGIONS ── */}

      {/* Neck */}
      <path d="M112 64 Q110 75 111 82 L129 82 Q130 75 128 64 Q122 60 118 60 Q114 60 112 64 Z"
        style={ms('neck')} onClick={() => onSelect('neck')}>
        <title>Neck</title>
      </path>

      {/* Left upper trap */}
      <path d="M110 80 Q95 82 80 88 Q68 94 64 102 Q72 106 82 108 Q94 106 104 100 Q108 92 110 84 Z"
        style={ms('traps_front')} onClick={() => onSelect('traps_front')}>
        <title>Upper Traps</title>
      </path>
      {/* Right upper trap */}
      <path d="M130 80 Q145 82 160 88 Q172 94 176 102 Q168 106 158 108 Q146 106 136 100 Q132 92 130 84 Z"
        style={ms('traps_front')} onClick={() => onSelect('traps_front')}>
        <title>Upper Traps</title>
      </path>

      {/* Left anterior deltoid */}
      <path d="M52 110 Q46 120 44 140 Q50 144 60 142 Q66 132 68 118 Q62 112 52 110 Z"
        style={ms('shoulders')} onClick={() => onSelect('shoulders')}>
        <title>Anterior Deltoid</title>
      </path>
      {/* Right anterior deltoid */}
      <path d="M188 110 Q194 120 196 140 Q190 144 180 142 Q174 132 172 118 Q178 112 188 110 Z"
        style={ms('shoulders')} onClick={() => onSelect('shoulders')}>
        <title>Anterior Deltoid</title>
      </path>

      {/* Left pec */}
      <path d="M78 100 Q68 108 66 126 Q65 144 68 160 Q80 166 96 164 Q108 160 112 150 Q112 130 110 114 Q98 104 86 100 Z"
        style={ms('chest')} onClick={() => onSelect('chest')}>
        <title>Chest (Left Pec)</title>
      </path>
      {/* Right pec */}
      <path d="M162 100 Q172 108 174 126 Q175 144 172 160 Q160 166 144 164 Q132 160 128 150 Q128 130 130 114 Q142 104 154 100 Z"
        style={ms('chest')} onClick={() => onSelect('chest')}>
        <title>Chest (Right Pec)</title>
      </path>

      {/* Left serratus (ribcage side finger marks) */}
      <path d="M64 156 Q60 168 60 184 Q60 196 62 208 Q68 210 74 206 Q76 194 76 180 Q76 166 74 156 Z"
        style={ms('serratus')} onClick={() => onSelect('serratus')}>
        <title>Serratus Anterior</title>
      </path>
      {/* Right serratus */}
      <path d="M176 156 Q180 168 180 184 Q180 196 178 208 Q172 210 166 206 Q164 194 164 180 Q164 166 166 156 Z"
        style={ms('serratus')} onClick={() => onSelect('serratus')}>
        <title>Serratus Anterior</title>
      </path>

      {/* Left bicep */}
      <path d="M40 138 Q36 156 36 178 Q38 196 42 214 Q48 218 56 216 Q60 196 60 176 Q60 156 58 138 Z"
        style={ms('biceps')} onClick={() => onSelect('biceps')}>
        <title>Biceps</title>
      </path>
      {/* Right bicep */}
      <path d="M200 138 Q204 156 204 178 Q202 196 198 214 Q192 218 184 216 Q180 196 180 176 Q180 156 182 138 Z"
        style={ms('biceps')} onClick={() => onSelect('biceps')}>
        <title>Biceps</title>
      </path>

      {/* Left forearm */}
      <path d="M36 238 Q32 260 33 290 Q34 306 36 314 L55 313 Q56 300 56 288 Q56 260 57 238 Z"
        style={ms('forearms')} onClick={() => onSelect('forearms')}>
        <title>Forearms</title>
      </path>
      {/* Right forearm */}
      <path d="M204 238 Q208 260 207 290 Q206 306 204 314 L185 313 Q184 300 184 288 Q184 260 183 238 Z"
        style={ms('forearms')} onClick={() => onSelect('forearms')}>
        <title>Forearms</title>
      </path>

      {/* Left oblique */}
      <path d="M66 158 Q62 180 62 206 Q62 222 64 238 Q70 242 78 240 Q80 224 80 206 Q80 180 78 158 Z"
        style={ms('obliques')} onClick={() => onSelect('obliques')}>
        <title>Obliques</title>
      </path>
      {/* Right oblique */}
      <path d="M174 158 Q178 180 178 206 Q178 222 176 238 Q170 242 162 240 Q160 224 160 206 Q160 180 162 158 Z"
        style={ms('obliques')} onClick={() => onSelect('obliques')}>
        <title>Obliques</title>
      </path>

      {/* Abs (rectus abdominis) — 6-pack grid */}
      <path d="M82 162 Q80 188 80 212 Q80 228 82 240 Q96 244 120 244 Q144 244 158 240 Q160 228 160 212 Q160 188 158 162 Q144 158 120 158 Q96 158 82 162 Z"
        style={ms('abs')} onClick={() => onSelect('abs')}>
        <title>Abs</title>
      </path>

      {/* Left hip flexor */}
      <path d="M80 240 Q76 256 74 272 Q74 282 76 288 Q86 292 96 290 Q100 278 100 264 Q100 250 98 240 Z"
        style={ms('hip_flexors')} onClick={() => onSelect('hip_flexors')}>
        <title>Hip Flexors</title>
      </path>
      {/* Right hip flexor */}
      <path d="M160 240 Q164 256 166 272 Q166 282 164 288 Q154 292 144 290 Q140 278 140 264 Q140 250 142 240 Z"
        style={ms('hip_flexors')} onClick={() => onSelect('hip_flexors')}>
        <title>Hip Flexors</title>
      </path>

      {/* Left quad (outer — vastus lateralis) */}
      <path d="M62 318 Q56 354 56 392 Q56 418 58 438 L80 438 Q82 420 82 390 Q82 354 84 318 Z"
        style={ms('quads')} onClick={() => onSelect('quads')}>
        <title>Quads</title>
      </path>
      {/* Right quad (outer) */}
      <path d="M178 318 Q184 354 184 392 Q184 418 182 438 L160 438 Q158 420 158 390 Q158 354 156 318 Z"
        style={ms('quads')} onClick={() => onSelect('quads')}>
        <title>Quads</title>
      </path>
      {/* Left quad inner (rectus femoris/VMO) */}
      <path d="M84 320 Q82 354 82 390 Q82 416 84 436 L100 436 Q102 416 102 390 Q102 354 100 320 Z"
        style={ms('quads')} onClick={() => onSelect('quads')}>
        <title>Quads (VMO)</title>
      </path>
      {/* Right quad inner */}
      <path d="M156 320 Q158 354 158 390 Q158 416 156 436 L140 436 Q138 416 138 390 Q138 354 140 320 Z"
        style={ms('quads')} onClick={() => onSelect('quads')}>
        <title>Quads (VMO)</title>
      </path>

      {/* Left adductor */}
      <path d="M86 316 Q82 345 82 376 Q82 406 84 432 L102 432 Q102 406 100 376 Q100 345 100 318 Z"
        style={ms('adductors')} onClick={() => onSelect('adductors')}>
        <title>Adductors</title>
      </path>
      {/* Right adductor */}
      <path d="M154 316 Q158 345 158 376 Q158 406 156 432 L140 432 Q140 406 140 376 Q140 345 140 318 Z"
        style={ms('adductors')} onClick={() => onSelect('adductors')}>
        <title>Adductors</title>
      </path>

      {/* Left tibialis (shin) */}
      <path d="M56 464 Q54 494 55 524 Q60 528 66 526 Q70 496 70 464 Z"
        style={ms('calves_front')} onClick={() => onSelect('calves_front')}>
        <title>Tibialis Anterior (Shin)</title>
      </path>
      {/* Right tibialis */}
      <path d="M184 464 Q186 494 185 524 Q180 528 174 526 Q170 496 170 464 Z"
        style={ms('calves_front')} onClick={() => onSelect('calves_front')}>
        <title>Tibialis Anterior (Shin)</title>
      </path>

      {/* ── Decorative anatomy lines ── */}
      {/* Pec separation line */}
      <line x1="120" y1="100" x2="120" y2="162" stroke="#b8a090" strokeWidth="0.6" strokeDasharray="2,2" opacity="0.5" />
      {/* Abs horizontal lines */}
      <path d="M84 182 Q102 186 120 186 Q138 186 156 182" fill="none" stroke="#b8a090" strokeWidth="0.6" opacity="0.4" />
      <path d="M83 208 Q102 212 120 212 Q138 212 157 208" fill="none" stroke="#b8a090" strokeWidth="0.6" opacity="0.4" />
      {/* Abs vertical center */}
      <line x1="120" y1="162" x2="120" y2="244" stroke="#b8a090" strokeWidth="0.6" strokeDasharray="2,2" opacity="0.4" />
      {/* Knee caps */}
      <ellipse cx="72" cy="452" rx="9" ry="7" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" opacity="0.6" />
      <ellipse cx="168" cy="452" rx="9" ry="7" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" opacity="0.6" />

      <text x="120" y="558" textAnchor="middle" fontSize="9" fill="#94a3b8" fontFamily="sans-serif" letterSpacing="2">FRONT</text>
    </svg>
  );
}
