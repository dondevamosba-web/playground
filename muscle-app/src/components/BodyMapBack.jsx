const SKIN = '#f2dfc8';
const SKIN_STROKE = '#c4956a';
const SKIN_DARK = '#e8c9a8';

export default function BodyMapBack({ getStyle, onSelect }) {
  const ms = getStyle;

  return (
    <svg viewBox="0 0 240 560" xmlns="http://www.w3.org/2000/svg"
      style={{ width: '100%', height: '100%', maxHeight: '100%' }}>

      {/* ── BODY OUTLINE (back view) ── */}

      {/* Head (back) */}
      <ellipse cx="120" cy="36" rx="24" ry="28" fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1.2" />
      <ellipse cx="96" cy="38" rx="4" ry="6" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" />
      <ellipse cx="144" cy="38" rx="4" ry="6" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" />

      {/* Neck */}
      <path d="M111 62 Q110 72 110 82 L130 82 Q130 72 129 62 Z" fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Main torso */}
      <path d="M110 80 Q85 82 68 92 Q52 102 50 118 Q48 138 52 158 Q56 178 60 202 Q63 224 64 252 Q66 268 68 282 L172 282 Q174 268 176 252 Q177 224 180 202 Q184 178 188 158 Q192 138 190 118 Q188 102 172 92 Q155 82 130 80 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1.2" />

      {/* Left upper arm */}
      <path d="M52 112 Q40 126 36 158 Q33 182 35 214 Q36 226 38 238 L56 236 Q57 224 58 212 Q58 182 62 158 Q66 130 68 114 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />
      {/* Right upper arm */}
      <path d="M188 112 Q200 126 204 158 Q207 182 205 214 Q204 226 202 238 L184 236 Q183 224 182 212 Q182 182 178 158 Q174 130 172 114 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left forearm back */}
      <path d="M38 236 Q32 258 32 288 Q32 304 34 316 L54 314 Q55 302 56 288 Q57 258 56 236 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />
      {/* Right forearm back */}
      <path d="M202 236 Q208 258 208 288 Q208 304 206 316 L186 314 Q185 302 184 288 Q183 258 184 236 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Hands */}
      <ellipse cx="43" cy="322" rx="10" ry="12" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" />
      <ellipse cx="197" cy="322" rx="10" ry="12" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" />

      {/* Hips/pelvis */}
      <path d="M68 280 Q62 300 62 318 L178 318 Q178 300 172 280 Z" fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left thigh back */}
      <path d="M62 316 Q56 354 55 392 Q54 418 56 440 L88 440 Q90 418 90 392 Q90 354 88 316 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />
      {/* Right thigh back */}
      <path d="M178 316 Q184 354 185 392 Q186 418 184 440 L152 440 Q150 418 150 392 Q150 354 152 316 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Knees */}
      <path d="M55 438 Q53 452 55 464 L88 464 Q90 452 90 438 Z" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="1" />
      <path d="M185 438 Q187 452 185 464 L152 464 Q150 452 150 438 Z" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Left lower leg */}
      <path d="M55 462 Q53 494 54 524 Q55 536 58 542 L84 542 Q86 536 86 524 Q86 494 86 462 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />
      {/* Right lower leg */}
      <path d="M185 462 Q187 494 186 524 Q185 536 182 542 L158 542 Q156 536 156 524 Q154 494 154 462 Z"
        fill={SKIN} stroke={SKIN_STROKE} strokeWidth="1" />

      {/* Feet */}
      <path d="M54 540 Q50 548 50 554 L82 554 Q84 552 86 542 Z" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.9" />
      <path d="M186 540 Q190 548 190 554 L158 554 Q156 552 154 542 Z" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.9" />

      {/* ── MUSCLE REGIONS ── */}

      {/* Neck back */}
      <path d="M112 64 Q110 75 111 82 L129 82 Q130 75 128 64 Q124 62 120 62 Q116 62 112 64 Z"
        style={ms('neck')} onClick={() => onSelect('neck')}>
        <title>Neck</title>
      </path>

      {/* Upper traps — large diamond shape across upper back */}
      <path d="M110 80 Q95 82 80 88 Q68 94 62 104 Q72 110 86 114 Q100 116 110 112 Q112 100 112 86 Z"
        style={ms('traps_front')} onClick={() => onSelect('traps_front')}>
        <title>Upper Traps (Left)</title>
      </path>
      <path d="M130 80 Q145 82 160 88 Q172 94 178 104 Q168 110 154 114 Q140 116 130 112 Q128 100 128 86 Z"
        style={ms('traps_front')} onClick={() => onSelect('traps_front')}>
        <title>Upper Traps (Right)</title>
      </path>

      {/* Rear deltoids */}
      <path d="M52 112 Q44 122 42 142 Q48 146 58 144 Q64 134 66 120 Q60 114 52 112 Z"
        style={ms('shoulders')} onClick={() => onSelect('shoulders')}>
        <title>Rear Deltoid</title>
      </path>
      <path d="M188 112 Q196 122 198 142 Q192 146 182 144 Q176 134 174 120 Q180 114 188 112 Z"
        style={ms('shoulders')} onClick={() => onSelect('shoulders')}>
        <title>Rear Deltoid</title>
      </path>

      {/* Rotator cuff / infraspinatus (shoulder blade area) */}
      <path d="M66 112 Q62 126 62 146 Q64 158 68 166 Q78 168 88 164 Q92 152 92 138 Q92 122 88 112 Z"
        style={ms('rotator_cuff')} onClick={() => onSelect('rotator_cuff')}>
        <title>Rotator Cuff / Infraspinatus</title>
      </path>
      <path d="M174 112 Q178 126 178 146 Q176 158 172 166 Q162 168 152 164 Q148 152 148 138 Q148 122 152 112 Z"
        style={ms('rotator_cuff')} onClick={() => onSelect('rotator_cuff')}>
        <title>Rotator Cuff / Infraspinatus</title>
      </path>

      {/* Mid traps / rhomboids (between shoulder blades) */}
      <path d="M90 112 Q86 130 86 152 Q88 164 92 172 Q106 174 120 174 Q134 174 148 172 Q152 164 154 152 Q154 130 150 112 Q136 118 120 118 Q104 118 90 112 Z"
        style={ms('upper_back')} onClick={() => onSelect('upper_back')}>
        <title>Mid Traps / Rhomboids</title>
      </path>

      {/* Left lat */}
      <path d="M62 158 Q58 180 60 210 Q62 228 64 244 Q72 248 80 244 Q82 228 82 208 Q82 180 80 158 Z"
        style={ms('lats')} onClick={() => onSelect('lats')}>
        <title>Lat (Left)</title>
      </path>
      {/* Right lat */}
      <path d="M178 158 Q182 180 180 210 Q178 228 176 244 Q168 248 160 244 Q158 228 158 208 Q158 180 160 158 Z"
        style={ms('lats')} onClick={() => onSelect('lats')}>
        <title>Lat (Right)</title>
      </path>

      {/* Lower traps */}
      <path d="M84 172 Q82 190 82 208 Q82 222 84 236 Q102 240 120 240 Q138 240 156 236 Q158 222 158 208 Q158 190 156 172 Q138 176 120 176 Q102 176 84 172 Z"
        style={ms('upper_back')} onClick={() => onSelect('upper_back')}>
        <title>Lower Traps</title>
      </path>

      {/* Erector spinae / lower back */}
      <path d="M88 238 Q85 258 85 278 L98 280 Q100 260 100 240 Z"
        style={ms('lower_back')} onClick={() => onSelect('lower_back')}>
        <title>Lower Back (Left)</title>
      </path>
      <path d="M152 238 Q155 258 155 278 L142 280 Q140 260 140 240 Z"
        style={ms('lower_back')} onClick={() => onSelect('lower_back')}>
        <title>Lower Back (Right)</title>
      </path>

      {/* Triceps left */}
      <path d="M40 140 Q36 160 36 182 Q37 200 40 218 Q46 222 55 220 Q58 200 58 180 Q58 160 60 140 Z"
        style={ms('triceps')} onClick={() => onSelect('triceps')}>
        <title>Triceps</title>
      </path>
      {/* Triceps right */}
      <path d="M200 140 Q204 160 204 182 Q203 200 200 218 Q194 222 185 220 Q182 200 182 180 Q182 160 180 140 Z"
        style={ms('triceps')} onClick={() => onSelect('triceps')}>
        <title>Triceps</title>
      </path>

      {/* Left forearm back */}
      <path d="M36 238 Q32 260 33 290 Q34 306 36 314 L55 313 Q56 300 56 288 Q56 260 57 238 Z"
        style={ms('forearms')} onClick={() => onSelect('forearms')}>
        <title>Forearms</title>
      </path>
      {/* Right forearm back */}
      <path d="M204 238 Q208 260 207 290 Q206 306 204 314 L185 313 Q184 300 184 288 Q184 260 183 238 Z"
        style={ms('forearms')} onClick={() => onSelect('forearms')}>
        <title>Forearms</title>
      </path>

      {/* Glutes — two lobes */}
      <path d="M66 282 Q60 298 60 316 L105 316 L105 290 Q92 284 80 282 Z"
        style={ms('glutes')} onClick={() => onSelect('glutes')}>
        <title>Glutes (Left)</title>
      </path>
      <path d="M174 282 Q180 298 180 316 L135 316 L135 290 Q148 284 160 282 Z"
        style={ms('glutes')} onClick={() => onSelect('glutes')}>
        <title>Glutes (Right)</title>
      </path>

      {/* Left hamstring */}
      <path d="M62 318 Q57 354 57 392 Q57 418 59 438 L88 438 Q90 418 90 392 Q90 354 86 318 Z"
        style={ms('hamstrings')} onClick={() => onSelect('hamstrings')}>
        <title>Hamstrings (Left)</title>
      </path>
      {/* Right hamstring */}
      <path d="M178 318 Q183 354 183 392 Q183 418 181 438 L152 438 Q150 418 150 392 Q150 354 154 318 Z"
        style={ms('hamstrings')} onClick={() => onSelect('hamstrings')}>
        <title>Hamstrings (Right)</title>
      </path>

      {/* Left calf — two heads */}
      <path d="M57 464 Q54 490 56 520 Q60 528 68 526 Q72 498 72 468 Z"
        style={ms('calves')} onClick={() => onSelect('calves')}>
        <title>Gastrocnemius (Left outer)</title>
      </path>
      <path d="M72 466 Q72 494 72 522 Q76 528 82 526 Q84 498 84 466 Z"
        style={ms('calves')} onClick={() => onSelect('calves')}>
        <title>Gastrocnemius (Left inner)</title>
      </path>
      {/* Right calf */}
      <path d="M183 464 Q186 490 184 520 Q180 528 172 526 Q168 498 168 468 Z"
        style={ms('calves')} onClick={() => onSelect('calves')}>
        <title>Gastrocnemius (Right outer)</title>
      </path>
      <path d="M168 466 Q168 494 168 522 Q164 528 158 526 Q156 498 156 466 Z"
        style={ms('calves')} onClick={() => onSelect('calves')}>
        <title>Gastrocnemius (Right inner)</title>
      </path>

      {/* ── Decorative lines ── */}
      {/* Spine line */}
      <line x1="120" y1="82" x2="120" y2="282" stroke="#b8a090" strokeWidth="0.7" strokeDasharray="3,3" opacity="0.4" />
      {/* Shoulder blade outline hints */}
      <path d="M88 116 Q84 134 86 154 Q92 158 100 156 Q96 136 96 116 Z" fill="none" stroke="#b8a090" strokeWidth="0.6" opacity="0.3" />
      <path d="M152 116 Q156 134 154 154 Q148 158 140 156 Q144 136 144 116 Z" fill="none" stroke="#b8a090" strokeWidth="0.6" opacity="0.3" />
      {/* Glute division line */}
      <line x1="120" y1="282" x2="120" y2="316" stroke="#b8a090" strokeWidth="0.8" opacity="0.35" />
      {/* Hamstring division lines */}
      <line x1="74" y1="320" x2="74" y2="436" stroke="#b8a090" strokeWidth="0.5" strokeDasharray="2,3" opacity="0.3" />
      <line x1="166" y1="320" x2="166" y2="436" stroke="#b8a090" strokeWidth="0.5" strokeDasharray="2,3" opacity="0.3" />
      {/* Knee caps back */}
      <ellipse cx="72" cy="452" rx="9" ry="7" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" opacity="0.6" />
      <ellipse cx="168" cy="452" rx="9" ry="7" fill={SKIN_DARK} stroke={SKIN_STROKE} strokeWidth="0.8" opacity="0.6" />

      <text x="120" y="558" textAnchor="middle" fontSize="9" fill="#94a3b8" fontFamily="sans-serif" letterSpacing="2">BACK</text>
    </svg>
  );
}
