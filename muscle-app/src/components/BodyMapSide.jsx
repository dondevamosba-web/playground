// flipped=false → body's left side (front faces right)
// flipped=true  → body's right side (front faces left, mirrored)
const SKIN = '#f2dfc8';
const SK = '#c4956a';
const SKD = '#e8c9a8';

export default function BodyMapSide({ getStyle, onSelect, flipped = false }) {
  const ms = getStyle;

  // front of body = right (x large), back = left (x small)
  // flipped mirrors this for the other side
  const scale = flipped ? 'scale(-1,1) translate(-240,0)' : undefined;

  return (
    <svg viewBox="0 0 240 560" xmlns="http://www.w3.org/2000/svg"
      style={{ width: '100%', height: '100%', maxHeight: '100%' }}>
      <g transform={scale}>

        {/* ── BODY OUTLINE (side profile) ── */}

        {/* Head — oval tilted slightly forward */}
        <ellipse cx="126" cy="34" rx="20" ry="26" fill={SKIN} stroke={SK} strokeWidth="1.2" />
        {/* Chin/jaw protrusion (front) */}
        <path d="M138 44 Q148 50 146 58 Q140 62 134 60 Q130 52 132 46 Z" fill={SKIN} stroke={SK} strokeWidth="0.8" />
        {/* Back of head */}
        <path d="M108 28 Q104 36 106 48 Q110 54 118 56" fill="none" stroke={SK} strokeWidth="1" />

        {/* Neck — leans forward slightly */}
        <path d="M118 58 Q116 68 116 80 L130 80 Q132 70 134 60 Z" fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Torso — S-curve profile: chest protrudes front, waist in, glute out back */}
        <path d="
          M116 78
          Q106 82 100 92
          Q94 104 92 120
          Q90 138 92 158
          Q94 175 96 195
          Q97 215 96 235
          Q95 255 93 270
          Q91 282 90 295
          L148 295
          Q148 280 148 265
          Q148 248 147 230
          Q146 210 146 192
          Q148 170 150 150
          Q152 128 150 108
          Q148 94 144 84
          Q136 78 126 78 Z"
          fill={SKIN} stroke={SK} strokeWidth="1.2" />

        {/* Chest protrusion (front) */}
        <path d="M148 106 Q156 118 156 136 Q156 152 150 162 Q148 148 148 130 Q148 116 148 106 Z"
          fill={SKIN} stroke={SK} strokeWidth="0.9" />

        {/* Shoulder mound */}
        <path d="M94 98 Q84 104 80 118 Q80 132 88 138 Q92 130 92 118 Q92 108 94 98 Z"
          fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Upper arm (hanging forward of hip) */}
        <path d="M82 132 Q76 158 76 188 Q76 210 78 232 L96 230 Q96 208 96 186 Q96 158 94 134 Z"
          fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Forearm */}
        <path d="M78 232 Q74 258 74 286 Q74 300 76 310 L94 308 Q95 296 95 284 Q95 258 96 232 Z"
          fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Hand */}
        <ellipse cx="84" cy="318" rx="9" ry="12" fill={SKD} stroke={SK} strokeWidth="0.8" />

        {/* Glute protrusion (back) */}
        <path d="M90 262 Q84 278 83 296 Q83 306 86 312 L100 312 Q100 300 100 288 Q100 272 96 262 Z"
          fill={SKIN} stroke={SK} strokeWidth="0.9" />

        {/* Hip / pelvis front */}
        <path d="M148 293 Q150 306 150 318 L100 318 Q100 306 100 293 Z"
          fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Front of thigh */}
        <path d="M148 316 Q152 350 152 390 Q152 418 150 440 L128 440 Q128 418 128 390 Q128 350 126 316 Z"
          fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Back of thigh */}
        <path d="M100 318 Q96 352 95 390 Q94 418 96 440 L126 440 Q128 418 128 390 Q128 352 126 318 Z"
          fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Knee */}
        <path d="M95 438 Q93 452 96 464 L152 464 Q154 452 152 438 Z"
          fill={SKD} stroke={SK} strokeWidth="1" />

        {/* Front lower leg (tibia area) */}
        <path d="M148 462 Q150 492 149 524 Q148 536 146 542 L128 542 Q128 532 128 520 Q128 490 126 462 Z"
          fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Back of lower leg (calf bulge) */}
        <path d="M96 464 Q92 492 93 520 Q94 534 98 542 L128 542 Q128 532 128 520 Q128 490 126 462 Z"
          fill={SKIN} stroke={SK} strokeWidth="1" />

        {/* Foot — extends forward (front of foot to the right) */}
        <path d="M98 540 Q96 550 96 556 L158 556 Q160 552 158 542 L128 542 Z"
          fill={SKD} stroke={SK} strokeWidth="0.9" />

        {/* Heel (back) */}
        <path d="M96 540 Q88 548 88 556 L98 556 L96 540 Z"
          fill={SKD} stroke={SK} strokeWidth="0.8" />


        {/* ── MUSCLE REGIONS ── */}

        {/* Neck */}
        <path d="M119 60 Q117 70 117 80 L131 80 Q132 70 134 62 Q128 58 122 58 Z"
          style={ms('neck')} onClick={() => onSelect('neck')}>
          <title>Neck</title>
        </path>

        {/* Rear delt / shoulder */}
        <path d="M94 96 Q84 104 80 120 Q80 134 88 140 Q94 132 94 118 Q94 106 96 96 Z"
          style={ms('shoulders')} onClick={() => onSelect('shoulders')}>
          <title>Deltoid</title>
        </path>
        {/* Anterior delt (front) */}
        <path d="M144 86 Q152 96 156 112 Q156 126 152 134 Q148 126 148 112 Q148 98 146 88 Z"
          style={ms('shoulders')} onClick={() => onSelect('shoulders')}>
          <title>Anterior Deltoid</title>
        </path>

        {/* Tricep (back of upper arm) */}
        <path d="M80 134 Q76 158 76 188 Q78 206 82 224 L92 222 Q92 204 92 184 Q92 158 92 134 Z"
          style={ms('triceps')} onClick={() => onSelect('triceps')}>
          <title>Triceps</title>
        </path>

        {/* Bicep (front of upper arm — narrow strip on front side) */}
        <path d="M94 136 Q96 158 96 186 Q96 206 96 224 L88 222 Q88 204 88 184 Q88 158 88 136 Z"
          style={ms('biceps')} onClick={() => onSelect('biceps')}>
          <title>Biceps</title>
        </path>

        {/* Forearm */}
        <path d="M76 234 Q72 260 73 288 Q74 302 76 310 L95 308 Q96 298 95 284 Q95 258 96 234 Z"
          style={ms('forearms')} onClick={() => onSelect('forearms')}>
          <title>Forearms</title>
        </path>

        {/* Lat (wide muscle on the side of torso) */}
        <path d="M92 132 Q88 156 88 184 Q88 210 90 234 Q98 238 106 234 Q108 210 108 184 Q108 156 106 132 Z"
          style={ms('lats')} onClick={() => onSelect('lats')}>
          <title>Lats</title>
        </path>

        {/* Serratus (front of ribs, side view) */}
        <path d="M142 152 Q148 164 148 184 Q148 200 146 216 Q140 220 134 216 Q132 200 132 184 Q132 164 136 152 Z"
          style={ms('serratus')} onClick={() => onSelect('serratus')}>
          <title>Serratus Anterior</title>
        </path>

        {/* Upper back / traps (back of torso) */}
        <path d="M92 96 Q96 112 96 132 L106 130 Q106 110 104 96 Z"
          style={ms('upper_back')} onClick={() => onSelect('upper_back')}>
          <title>Upper Traps / Rhomboids</title>
        </path>

        {/* Lower back (erectors, visible from side) */}
        <path d="M91 198 Q90 220 90 244 Q92 258 96 270 Q102 272 108 268 Q108 252 108 234 Q108 212 106 196 Z"
          style={ms('lower_back')} onClick={() => onSelect('lower_back')}>
          <title>Lower Back</title>
        </path>

        {/* Glute (side view) */}
        <path d="M90 264 Q84 278 83 296 Q84 310 90 316 L110 316 Q110 304 110 292 Q110 274 106 264 Z"
          style={ms('glutes')} onClick={() => onSelect('glutes')}>
          <title>Glutes</title>
        </path>

        {/* Hip flexor (front of hip, TFL) */}
        <path d="M144 248 Q148 268 148 290 Q148 304 148 316 L130 316 Q130 302 130 288 Q130 266 132 250 Z"
          style={ms('hip_flexors')} onClick={() => onSelect('hip_flexors')}>
          <title>Hip Flexors / TFL</title>
        </path>

        {/* Quad (front of thigh) */}
        <path d="M148 318 Q152 352 152 390 Q152 418 150 438 L128 438 Q128 418 128 390 Q128 350 128 318 Z"
          style={ms('quads')} onClick={() => onSelect('quads')}>
          <title>Quads</title>
        </path>

        {/* Hamstring (back of thigh) */}
        <path d="M100 320 Q96 354 95 390 Q94 418 96 438 L126 438 Q128 418 128 390 Q128 354 128 320 Z"
          style={ms('hamstrings')} onClick={() => onSelect('hamstrings')}>
          <title>Hamstrings</title>
        </path>

        {/* Calf / gastrocnemius (back of lower leg) */}
        <path d="M96 466 Q92 494 93 522 Q96 532 102 536 L122 536 Q124 528 124 518 Q124 490 126 466 Z"
          style={ms('calves')} onClick={() => onSelect('calves')}>
          <title>Calves</title>
        </path>

        {/* Tibialis (front of shin) */}
        <path d="M148 464 Q150 494 149 524 Q148 534 144 540 L130 540 Q130 528 130 516 Q130 488 128 464 Z"
          style={ms('calves_front')} onClick={() => onSelect('calves_front')}>
          <title>Tibialis Anterior</title>
        </path>

        {/* ── Decorative lines ── */}
        <line x1="119" y1="80" x2="116" y2="295" stroke="#b8a090" strokeWidth="0.6" strokeDasharray="3,4" opacity="0.35" />
        <ellipse cx="122" cy="452" rx="10" ry="7" fill={SKD} stroke={SK} strokeWidth="0.8" opacity="0.55" />

        <text x="120" y="559" textAnchor="middle" fontSize="9" fill="#94a3b8" fontFamily="sans-serif" letterSpacing="2">
          {flipped ? 'RIGHT SIDE' : 'LEFT SIDE'}
        </text>
      </g>
    </svg>
  );
}
