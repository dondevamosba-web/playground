export const muscles = {
  // FRONT
  neck: {
    id: 'neck',
    name: 'Neck',
    view: 'front',
    color: '#a8c5da',
    description: 'Cervical muscles that support and move the head.',
    worked: {
      stretch: [
        { name: 'Chin Tucks', how: 'Gently pull your chin straight back, holding 5s. 10 reps.', duration: '2 min' },
        { name: 'Side Neck Stretch', how: 'Tilt ear to shoulder, hold 30s each side.', duration: '1 min' },
        { name: 'Neck Rotation', how: 'Slowly turn head left and right, 10 reps each side.', duration: '2 min' },
      ],
      rest: 'Avoid heavy overhead pressing for 24–48h. Use a supportive pillow.',
      strengthen: [
        { name: 'Isometric Neck Press', how: 'Press hand against forehead with resistance for 5s. 3 sets of 10.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Poor posture', 'Sleeping position', 'Text neck', 'Muscle strain from exercise'],
      immediate: [
        { name: 'Ice/Heat', how: 'Ice first 48h for acute pain, heat after. 15–20 min each session.' },
        { name: 'Gentle Range-of-Motion', how: 'Slow circles and side-to-side tilts. Stop if sharp pain.' },
      ],
      stretch: [
        { name: 'Upper Trap Stretch', how: 'Tilt head to one side, use hand for gentle overpressure. 30s per side.' },
        { name: 'Levator Scapula Stretch', how: 'Turn head 45° and look down into armpit. 30s per side.' },
      ],
      strengthen: [
        { name: 'Deep Neck Flexor Activation', how: 'Lying on back, nod chin gently without lifting head. 10 reps x 3.' },
      ],
      see_doctor: 'If pain radiates into arm, causes numbness/tingling, or follows trauma.',
    },
  },

  traps_front: {
    id: 'traps_front',
    name: 'Upper Traps',
    view: 'front',
    color: '#a8c5da',
    description: 'Upper trapezius — elevates shoulders and supports the neck.',
    worked: {
      stretch: [
        { name: 'Cross-Body Shoulder Stretch', how: 'Pull arm across chest, hold 30s each side.', duration: '1 min' },
        { name: 'Upper Trap Stretch', how: 'Tilt ear to shoulder, hold 30s each side.', duration: '1 min' },
      ],
      rest: 'Avoid shrugging movements for 24h. Roll shoulders back periodically.',
      strengthen: [
        { name: 'Shoulder Shrugs', how: 'With dumbbells, shrug up and hold 2s. 3x12.', duration: '5 min' },
        { name: 'Face Pulls', how: 'Pull rope to face level with elbows flared. 3x15.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Carrying heavy bags', 'Stress/tension', 'Poor desk posture', 'Overloaded shrugs'],
      immediate: [
        { name: 'Self-Massage', how: 'Use fingers or a ball to roll out the upper trap for 2–3 min per side.' },
        { name: 'Heat Therapy', how: 'Apply warm pad to upper traps for 15 min to release tension.' },
      ],
      stretch: [
        { name: 'Neck Tilt Stretch', how: 'Look straight ahead, tilt ear to shoulder with light hand pressure. 30s.' },
        { name: 'Thread the Needle', how: 'On all fours, thread one arm under body and rotate. 30s per side.' },
      ],
      strengthen: [
        { name: 'Y-T-W Raises', how: 'Lying prone, raise arms in Y, T, and W shapes. 3x10 each.', duration: '6 min' },
      ],
      see_doctor: 'If pain is persistent >2 weeks, or accompanied by headaches and dizziness.',
    },
  },

  chest: {
    id: 'chest',
    name: 'Chest (Pectorals)',
    view: 'front',
    color: '#a8c5da',
    description: 'Pectoralis major and minor — responsible for pushing and horizontal pressing.',
    worked: {
      stretch: [
        { name: 'Doorway Chest Stretch', how: 'Place forearm on door frame, rotate away. Hold 30s each side.', duration: '2 min' },
        { name: 'Pec Deck Reverse', how: 'Clasp hands behind back, squeeze shoulder blades, lift slightly. Hold 20s.', duration: '1 min' },
        { name: 'Corner Stretch', how: 'Face a corner, hands on walls at shoulder height, lean in gently. 30s.', duration: '1 min' },
      ],
      rest: 'Avoid pressing or push-up variations for 48h. Focus on pulling movements instead.',
      strengthen: [
        { name: 'Cable Flyes', how: 'Keep slight bend in elbows, bring cables together in an arc. 3x12.', duration: '6 min' },
        { name: 'Push-Up Variations', how: 'Wide-grip, diamond, or incline push-ups to hit different angles. 3x10–15.', duration: '8 min' },
      ],
    },
    hurts: {
      likely_causes: ['Overuse from pressing', 'Muscle strain', 'Pectoralis minor tightness from desk work', 'AC joint issue'],
      immediate: [
        { name: 'Rest & Ice', how: 'Apply ice for 15–20 min within first 48h of strain.' },
        { name: 'Gentle Self-Massage', how: 'Use fingertips to roll out pec minor (below collarbone) in circles.' },
      ],
      stretch: [
        { name: 'Doorway Stretch', how: 'Both arms on frame, step through. Hold 30s. Feel stretch in chest, not shoulder.' },
        { name: 'Foam Roller T-Spine', how: 'Lay roller perpendicular to spine mid-back, arms behind head, open chest.' },
      ],
      strengthen: [
        { name: 'Band Pull-Aparts', how: 'Hold band in front, pull apart to open chest. 3x20.', duration: '4 min' },
        { name: 'Serratus Wall Slides', how: 'Forearms on wall, slide up while pushing into wall. 3x10.', duration: '5 min' },
      ],
      see_doctor: 'If you felt a pop/tear, have significant swelling, or can\'t raise arm.',
    },
  },

  shoulders: {
    id: 'shoulders',
    name: 'Shoulders (Deltoids)',
    view: 'front',
    color: '#a8c5da',
    description: 'Anterior, lateral, and posterior deltoids — control arm elevation and rotation.',
    worked: {
      stretch: [
        { name: 'Cross-Body Shoulder Stretch', how: 'Pull arm across chest at shoulder height. Hold 30s each side.', duration: '1 min' },
        { name: 'Overhead Tricep/Shoulder Stretch', how: 'Reach arm overhead, bend at elbow, use other hand for pressure. 30s.', duration: '1 min' },
        { name: 'Sleeper Stretch', how: 'Lie on sore shoulder, push forearm toward bed gently. 30s each side.', duration: '1 min' },
      ],
      rest: 'Avoid overhead pressing for 24–48h. Sub in lateral raises at lighter weights.',
      strengthen: [
        { name: 'Lateral Raises', how: 'Light weight, raise arms to shoulder height. 3x15.', duration: '5 min' },
        { name: 'Face Pulls', how: 'Pull to face height with elbows high. Builds rear delt and rotator cuff. 3x15.', duration: '5 min' },
        { name: 'Arnold Press', how: 'Start palms facing you, rotate as you press. 3x10.', duration: '6 min' },
      ],
    },
    hurts: {
      likely_causes: ['Rotator cuff strain', 'Shoulder impingement', 'Overuse from overhead work', 'AC joint sprain'],
      immediate: [
        { name: 'Ice', how: '15–20 min every 2h for acute pain/swelling.' },
        { name: 'Pendulum Exercise', how: 'Lean forward, let arm hang, make small circles. Gentle traction relieves pressure.' },
      ],
      stretch: [
        { name: 'Sleeper Stretch', how: 'Best for posterior capsule tightness. Push forearm gently toward floor. 30s.' },
        { name: 'Cross-Body Stretch', how: 'Focus on feeling it in the back of the shoulder, not the front.' },
      ],
      strengthen: [
        { name: 'External Rotation with Band', how: 'Elbow at 90°, rotate forearm outward against band. 3x15.', duration: '5 min' },
        { name: 'Side-Lying ER', how: 'Lying on side, rotate dumbbell up from hip. 3x12.', duration: '5 min' },
        { name: 'Band Pull-Aparts', how: '3x20 — crucial for shoulder health and posture.', duration: '4 min' },
      ],
      see_doctor: 'If pain is over AC joint (top of shoulder), arm goes numb, or you can\'t raise arm past 90°.',
    },
  },

  biceps: {
    id: 'biceps',
    name: 'Biceps',
    view: 'front',
    color: '#a8c5da',
    description: 'Biceps brachii — flexes the elbow and supinates the forearm.',
    worked: {
      stretch: [
        { name: 'Wall Bicep Stretch', how: 'Extend arm against wall, thumb down, rotate away. Hold 30s.', duration: '1 min' },
        { name: 'Behind-Back Clasp', how: 'Clasp hands behind back, extend arms and lift slightly. 30s.', duration: '1 min' },
      ],
      rest: 'Avoid heavy curl movements for 48h. Keep pulling volume low.',
      strengthen: [
        { name: 'Hammer Curls', how: 'Neutral grip. 3x10–12. Builds brachialis underneath.', duration: '5 min' },
        { name: 'Incline Dumbbell Curls', how: 'Lean back on incline bench, full stretch at bottom. 3x10.', duration: '6 min' },
        { name: 'Chin-Ups', how: 'Supinated grip pull-up. 3 sets to comfortable failure.', duration: '8 min' },
      ],
    },
    hurts: {
      likely_causes: ['DOMS from curls', 'Distal bicep tendinopathy', 'Overuse from pulling/rowing', 'Strain at elbow attachment'],
      immediate: [
        { name: 'Rest & Ice', how: 'Ice at the elbow attachment if tender there. 15 min every 2h.' },
        { name: 'Contrast Bathing', how: 'Alternate warm and cold water on forearm/elbow area. 3 rounds.' },
      ],
      stretch: [
        { name: 'Wall Stretch', how: 'Arm extended, thumb pointing down, rotate body away slowly.' },
        { name: 'Tabletop Stretch', how: 'Hands on table, fingers pointing back toward you, lean forward gently.' },
      ],
      strengthen: [
        { name: 'Eccentric Curls', how: 'Use 2 arms to curl up, lower with 1 arm slowly (4 counts). 3x8 each arm.', duration: '6 min' },
        { name: 'Supination Drills', how: 'Hold light dumbbell, rotate palm up and down slowly. 3x15.', duration: '4 min' },
      ],
      see_doctor: 'If you felt a pop near elbow (possible tendon tear), or have a visible "Popeye" deformity.',
    },
  },

  forearms: {
    id: 'forearms',
    name: 'Forearms',
    view: 'front',
    color: '#a8c5da',
    description: 'Flexors and extensors that control wrist and grip.',
    worked: {
      stretch: [
        { name: 'Wrist Flexor Stretch', how: 'Extend arm, palm up, use other hand to pull fingers back. 30s.', duration: '1 min' },
        { name: 'Wrist Extensor Stretch', how: 'Extend arm, palm down, pull fingers toward you. 30s.', duration: '1 min' },
        { name: 'Prayer Stretch', how: 'Press palms together, push down until you feel forearm stretch. 30s.', duration: '1 min' },
      ],
      rest: 'Grip-intensive work should be avoided for 24h. Contrast showers help.',
      strengthen: [
        { name: 'Farmer Carries', how: 'Walk 20–30m with heavy dumbbells. 3 sets.', duration: '6 min' },
        { name: 'Plate Pinches', how: 'Pinch 2 plates together by thumb and fingers. Hold 20s. 3 sets.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Tennis elbow (lateral epicondylitis)', 'Golfer\'s elbow (medial)', 'Repetitive strain', 'Keyboard/mouse overuse'],
      immediate: [
        { name: 'Ice at Elbow', how: 'Apply ice to the tender spot on the elbow. 15 min, 3x per day.' },
        { name: 'Forearm Massage', how: 'Use thumb to work down the belly of the forearm, 2 min each side.' },
      ],
      stretch: [
        { name: 'Flexor Stretch', how: 'Arm out, palm up, pull fingers back. If lateral elbow hurts, also try palm-down version.' },
        { name: 'Towel Wring', how: 'Hold small towel with both hands, twist it in opposite directions. 20 reps.' },
      ],
      strengthen: [
        { name: 'Eccentric Wrist Extension', how: 'Use other hand to curl weight up, lower slowly with injured side. 3x15.', duration: '5 min' },
        { name: 'Stress Ball Squeezes', how: 'Squeeze slowly 30 times, 3 sets.', duration: '3 min' },
      ],
      see_doctor: 'If pain persists >6 weeks, or is near the bone rather than the muscle belly.',
    },
  },

  abs: {
    id: 'abs',
    name: 'Abs (Core)',
    view: 'front',
    color: '#a8c5da',
    description: 'Rectus abdominis, transverse abdominis — spine stability and trunk flexion.',
    worked: {
      stretch: [
        { name: 'Cobra Pose', how: 'Lie prone, press up with arms, let hips stay on ground. Hold 30s. 3 reps.', duration: '2 min' },
        { name: 'Full-Body Extension', how: 'Lying on back, reach arms overhead and stretch long. Hold 20s.', duration: '1 min' },
        { name: 'Cat-Cow', how: '10 slow reps to mobilize the entire spine.', duration: '2 min' },
      ],
      rest: 'Avoid direct core work for 48h after intense ab sessions. Brace during daily movements.',
      strengthen: [
        { name: 'Dead Bug', how: 'Lower opposite arm and leg while pressing low back to floor. 3x10 each side.', duration: '6 min' },
        { name: 'Pallof Press', how: 'Anti-rotation hold with cable/band. 3x10 each side.', duration: '6 min' },
        { name: 'Plank Variations', how: 'Standard, side plank, RKC plank. 3 sets of 30–60s each.', duration: '8 min' },
      ],
    },
    hurts: {
      likely_causes: ['DOMS from crunches/sit-ups', 'Muscle strain', 'Hernia (refer to doctor)', 'Hip flexor tightness mimicking ab pain'],
      immediate: [
        { name: 'Rest', how: 'Avoid any trunk flexion for 48h if sharp pain.' },
        { name: 'Diaphragmatic Breathing', how: 'Deep belly breaths help release abdominal tension. 10 slow breaths.' },
      ],
      stretch: [
        { name: 'Cobra Pose', how: 'Gentle extension to counteract flexion strain. 3x20s.' },
        { name: 'Child\'s Pose', how: 'Arms overhead, hips back. 30–60s. Decompresses spine.' },
      ],
      strengthen: [
        { name: 'Glute Bridge', how: 'Feet flat, drive hips up, squeeze glutes. Takes pressure off abs. 3x15.', duration: '5 min' },
        { name: 'Bird Dog', how: 'On all fours, extend opposite arm + leg. 3x10.', duration: '5 min' },
      ],
      see_doctor: 'If pain is sharp, severe, or accompanied by nausea — could indicate hernia or organ issue.',
    },
  },

  obliques: {
    id: 'obliques',
    name: 'Obliques',
    view: 'front',
    color: '#a8c5da',
    description: 'Internal and external obliques — trunk rotation and lateral flexion.',
    worked: {
      stretch: [
        { name: 'Side Bend Stretch', how: 'Stand tall, reach arm overhead and lean to opposite side. 30s each.', duration: '2 min' },
        { name: 'Seated Twist', how: 'Sit on floor, cross one leg, rotate toward bent knee. 30s each side.', duration: '2 min' },
      ],
      rest: 'Avoid rotational movements for 24–48h.',
      strengthen: [
        { name: 'Russian Twists', how: 'Seated, feet up, rotate side to side with weight. 3x20.', duration: '5 min' },
        { name: 'Woodchops', how: 'Cable diagonal pull from high to low (and reverse). 3x12 each.', duration: '6 min' },
        { name: 'Side Plank', how: 'Hold body in a line on one forearm. 3x30–45s each.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Rotational overload', 'Side stitch during running', 'Rib stress (rare)', 'DOMS from twisting exercises'],
      immediate: [
        { name: 'Rest from Rotation', how: 'Stop any twisting movements for 48h.' },
        { name: 'Ice the Side', how: 'If strain is localized, ice for 15 min.' },
      ],
      stretch: [
        { name: 'Side Bend', how: 'Lean to the non-painful side to stretch the sore oblique. Hold 30s.' },
        { name: 'Supine Twist', how: 'Lie on back, bring knee across body. Hold 30s each side.' },
      ],
      strengthen: [
        { name: 'Side Plank', how: 'Start with short holds (15s), build up. Don\'t push through pain.', duration: '4 min' },
      ],
      see_doctor: 'If pain is over the rib itself (not the muscle), or sharp and worsens with breathing.',
    },
  },

  hip_flexors: {
    id: 'hip_flexors',
    name: 'Hip Flexors',
    view: 'front',
    color: '#a8c5da',
    description: 'Iliopsoas and rectus femoris — lift the knee and flex the hip.',
    worked: {
      stretch: [
        { name: 'Kneeling Hip Flexor Lunge', how: 'Drop to one knee, push hip forward gently. Hold 45–60s each side.', duration: '3 min' },
        { name: 'Pigeon Pose', how: 'Front shin on ground, lean forward over it. Hold 60s each side.', duration: '4 min' },
        { name: 'Couch Stretch', how: 'Shin against wall behind you, knee on ground. 45s each side.', duration: '3 min' },
      ],
      rest: 'Avoid running, lunges, or climbing stairs aggressively for 24h.',
      strengthen: [
        { name: 'Hanging Knee Raises', how: 'Hang from bar, bring knees to chest. 3x12.', duration: '5 min' },
        { name: 'Psoas March', how: 'Lying on back, alternate lifting knees while bracing core. 3x10.', duration: '4 min' },
      ],
    },
    hurts: {
      likely_causes: ['Tight hip flexors from sitting', 'Overuse from sprinting/kicking', 'Hip impingement', 'Stress fracture (rare)'],
      immediate: [
        { name: 'Avoid Aggravating Movements', how: 'No running, kicking, or deep lunges until pain subsides.' },
        { name: 'Ice the Front Hip', how: '15 min, especially after activity.' },
      ],
      stretch: [
        { name: 'Kneeling Lunge Stretch', how: 'Hold 60s. This is the #1 release for tight hip flexors from sitting.' },
        { name: 'Thomas Test Stretch', how: 'Lie on table edge, pull one knee to chest, let other leg hang. 30s.' },
      ],
      strengthen: [
        { name: 'Glute Bridges', how: 'Activating glutes reduces hip flexor dominance. 3x20.', duration: '5 min' },
        { name: 'Hip Flexor Isometric', how: 'Standing, push knee into hand at 90°. Hold 10s. 3x10.', duration: '4 min' },
      ],
      see_doctor: 'If you hear a snap/click with pain (snapping hip syndrome), or deep groin pain.',
    },
  },

  quads: {
    id: 'quads',
    name: 'Quads',
    view: 'front',
    color: '#a8c5da',
    description: 'Quadriceps femoris — extends the knee and stabilizes the patella.',
    worked: {
      stretch: [
        { name: 'Standing Quad Stretch', how: 'Hold ankle behind you, keep knees together. Hold 45s each side.', duration: '2 min' },
        { name: 'Couch Stretch', how: 'Knee on floor, foot up on couch behind. Best deep quad stretch. 60s each.', duration: '4 min' },
        { name: 'Rectus Femoris Stretch', how: 'Kneeling, tilt pelvis back while pulling ankle up. 45s.', duration: '2 min' },
      ],
      rest: 'Skip squats and lunges for 48h. Easy cycling at low resistance helps flush lactate.',
      strengthen: [
        { name: 'Bulgarian Split Squat', how: 'Rear foot elevated, drop down to 90°. 3x8 each side.', duration: '8 min' },
        { name: 'Spanish Squat', how: 'Lean back into band/pole, sit into deep squat. 3x15.', duration: '6 min' },
        { name: 'Leg Extension', how: 'Isolate VMO at end range. 3x12 light-to-moderate.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['DOMS from squats/lunges', 'Patellar tendinopathy', 'IT band syndrome', 'Quad strain'],
      immediate: [
        { name: 'Ice', how: '15–20 min at the tender spot, especially the patellar tendon area.' },
        { name: 'Foam Roll', how: 'Roll quad slowly, pause on tight spots for 20–30s each.' },
      ],
      stretch: [
        { name: 'Couch Stretch', how: 'Deepest quad stretch — hold 60s each side.' },
        { name: 'Low Lunge', how: 'Front foot forward, back knee on ground. Add hip shift for more hip flexor.' },
      ],
      strengthen: [
        { name: 'Isometric Wall Sit', how: 'At 60–90°, hold 30–45s. 3 sets. Excellent for patellar tendon rehab.', duration: '5 min' },
        { name: 'Eccentric Step-Down', how: 'Stand on step, lower other foot slowly on injured leg. 3x10.', duration: '6 min' },
      ],
      see_doctor: 'If pain is localized to kneecap or patellar tendon, worsens going downstairs, or knee locks/gives way.',
    },
  },

  calves_front: {
    id: 'calves_front',
    name: 'Tibialis Anterior',
    view: 'front',
    color: '#a8c5da',
    description: 'Front of lower leg — dorsiflexes the ankle.',
    worked: {
      stretch: [
        { name: 'Kneeling Shin Stretch', how: 'Kneel with feet flat, sit back on heels. Hold 30s.', duration: '1 min' },
        { name: 'Toe Drag', how: 'Standing, extend foot back on toes and drag forward. 15 reps.', duration: '2 min' },
      ],
      rest: 'Avoid running or walking on rough terrain for 24h.',
      strengthen: [
        { name: 'Tibialis Raises', how: 'Leaning against wall, raise toes off ground. 3x20.', duration: '4 min' },
        { name: 'Band Dorsiflexion', how: 'Band around foot arch, pull toes up against resistance. 3x15.', duration: '4 min' },
      ],
    },
    hurts: {
      likely_causes: ['Shin splints', 'Tibialis anterior tendinopathy', 'Overuse from running', 'Compartment syndrome (serious)'],
      immediate: [
        { name: 'Ice', how: '15 min on shin after activity.' },
        { name: 'Rest from Impact', how: 'No running until pain-free walking for 48h.' },
      ],
      stretch: [
        { name: 'Kneeling Shin Stretch', how: 'Sit on heels, toes pointed back. 30s.' },
      ],
      strengthen: [
        { name: 'Tibialis Raises', how: 'Back against wall, raise toes. 3x20. Key for shin splint prevention.', duration: '4 min' },
      ],
      see_doctor: 'If leg feels tight like a balloon, or pain is severe — could be compartment syndrome.',
    },
  },

  // BACK VIEW
  upper_back: {
    id: 'upper_back',
    name: 'Upper Back (Traps & Rhomboids)',
    view: 'back',
    color: '#a8c5da',
    description: 'Mid-trapezius, rhomboids — retract and stabilize shoulder blades.',
    worked: {
      stretch: [
        { name: 'Thread the Needle', how: 'On all fours, reach arm under body and rotate. 30s each side.', duration: '2 min' },
        { name: 'Seated Forward Fold', how: 'Round upper back, reach arms forward, breathe into shoulder blades. 30s.', duration: '1 min' },
        { name: 'Cat Stretch', how: 'On all fours, round upper back to ceiling. 10 slow reps.', duration: '2 min' },
      ],
      rest: 'Avoid heavy rowing for 48h. Focus on chest stretching to balance the work.',
      strengthen: [
        { name: 'Bent-Over Rows', how: 'Hinge at hips, pull bar/dumbbells to lower chest. 3x10.', duration: '6 min' },
        { name: 'Seated Cable Rows', how: 'Pull to belly button, squeeze shoulder blades. 3x12.', duration: '5 min' },
        { name: 'Band Pull-Aparts', how: 'Arms extended, pull band apart squeezing rhomboids. 3x20.', duration: '4 min' },
      ],
    },
    hurts: {
      likely_causes: ['Poor posture', 'Overuse from rowing', 'Rhomboid strain', 'Referred pain from neck'],
      immediate: [
        { name: 'Heat', how: 'Moist heat on upper back 15–20 min. Loosens tight muscles.' },
        { name: 'Foam Roll Thoracic Spine', how: 'Roll from mid to upper back, arms behind head. 2–3 min.' },
      ],
      stretch: [
        { name: 'Thread the Needle', how: 'Best stretch for rhomboids and upper back rotation. 45s each side.' },
        { name: 'Doorway Row Stretch', how: 'Hold door frame, lean back letting shoulder blade spread. 30s.' },
      ],
      strengthen: [
        { name: 'Face Pulls', how: 'Cable to face height, elbows high. 3x15. Essential for upper back health.', duration: '5 min' },
        { name: 'Y-T-W Raises', how: 'Prone on bench or floor, raise arms in each letter shape. 3x10.', duration: '5 min' },
      ],
      see_doctor: 'If pain is between shoulder blade and spine and doesn\'t improve, or if it refers down the arm.',
    },
  },

  lats: {
    id: 'lats',
    name: 'Lats',
    view: 'back',
    color: '#a8c5da',
    description: 'Latissimus dorsi — pulls the arm down and back, key for pull-ups.',
    worked: {
      stretch: [
        { name: 'Overhead Lat Stretch', how: 'Grab something overhead, lean to one side and push hip out. 30–45s.', duration: '2 min' },
        { name: 'Child\'s Pose with Side Reach', how: 'Walk hands to one side in child\'s pose. Hold 30s each.', duration: '2 min' },
        { name: 'Standing Side Reach', how: 'Reach arm overhead and lean away from it. 30s each side.', duration: '1 min' },
      ],
      rest: 'Avoid pull-ups and pulldowns for 48h. Prioritize thoracic mobility work.',
      strengthen: [
        { name: 'Pull-Ups / Chin-Ups', how: 'Full range of motion — dead hang to chin over bar. 3 sets to comfortable failure.', duration: '8 min' },
        { name: 'Straight-Arm Pulldown', how: 'Arms straight, pull bar from overhead to hips. Isolates lats. 3x12.', duration: '5 min' },
        { name: 'Single-Arm Dumbbell Row', how: 'Lean on bench, pull elbow toward hip (not shoulder). 3x10.', duration: '6 min' },
      ],
    },
    hurts: {
      likely_causes: ['Pull-up overuse', 'DOMS from rowing', 'Teres major strain', 'Lat tendinopathy at humerus'],
      immediate: [
        { name: 'Ice', how: '15 min on the side of the back/under armpit where it hurts.' },
        { name: 'Avoid Pull-Down Movements', how: 'Rest from all pulling for 48h.' },
      ],
      stretch: [
        { name: 'Child\'s Pose Side Reach', how: 'Walk both hands to sore side, let lat lengthen. 60s.' },
        { name: 'Hanging Stretch', how: 'Hang from bar with slight bend in elbow. Let lat decompress. 20–30s.' },
      ],
      strengthen: [
        { name: 'Lat Activation Drill', how: 'Hand against wall, push it away while tightening lat. 3x10 holds.', duration: '3 min' },
        { name: 'Banded Lat Pulldown', how: 'Light band, focus on lat engagement at full range. 3x15.', duration: '4 min' },
      ],
      see_doctor: 'If pain is at the top of the arm bone or armpit and doesn\'t respond to rest in 1–2 weeks.',
    },
  },

  triceps: {
    id: 'triceps',
    name: 'Triceps',
    view: 'back',
    color: '#a8c5da',
    description: 'Triceps brachii — extends the elbow, key for all pushing movements.',
    worked: {
      stretch: [
        { name: 'Overhead Tricep Stretch', how: 'Reach arm overhead, bend at elbow, use other hand to press. 30s each.', duration: '1 min' },
        { name: 'Wall Tricep Stretch', how: 'Place elbow on wall at 90°, rotate body away. 30s each.', duration: '1 min' },
      ],
      rest: 'Avoid pressing for 48h. Light band pull-aparts and rows are fine.',
      strengthen: [
        { name: 'Close-Grip Bench Press', how: 'Hands shoulder-width on bar, press with elbows tucked. 3x8.', duration: '6 min' },
        { name: 'Skull Crushers', how: 'Lower bar to forehead with elbows fixed. 3x10.', duration: '5 min' },
        { name: 'Tricep Dips', how: 'Dip bars or parallel bars, lean slightly forward. 3 sets to failure.', duration: '6 min' },
      ],
    },
    hurts: {
      likely_causes: ['Overuse from pressing', 'Tricep tendinopathy at elbow', 'Lateral head strain', 'Olecranon bursitis'],
      immediate: [
        { name: 'Ice', how: 'Especially at the back of the elbow if that\'s where it hurts. 15 min.' },
        { name: 'Rest Pressing', how: 'No bench, overhead press, or dips for 48–72h.' },
      ],
      stretch: [
        { name: 'Overhead Stretch', how: 'Slow and gentle. Don\'t force range of motion if sharp pain.' },
      ],
      strengthen: [
        { name: 'Eccentric Extensions', how: 'With band, resist extension. Lower slowly over 4 counts. 3x12.', duration: '4 min' },
        { name: 'Pushdown Holds', how: 'Hold at full extension for 2s each rep. Light weight. 3x12.', duration: '4 min' },
      ],
      see_doctor: 'If point tenderness at elbow tip (olecranon), significant swelling, or pain at rest.',
    },
  },

  lower_back: {
    id: 'lower_back',
    name: 'Lower Back (Erectors)',
    view: 'back',
    color: '#a8c5da',
    description: 'Erector spinae and multifidus — extend and stabilize the lumbar spine.',
    worked: {
      stretch: [
        { name: 'Child\'s Pose', how: 'Sit back on heels, arms forward. Hold 60s. Best low-back decompressor.', duration: '2 min' },
        { name: 'Knee-to-Chest', how: 'Lying on back, pull both knees to chest. Hold 30s.', duration: '1 min' },
        { name: 'Supine Twist', how: 'Bend knee, drop it across body with arm out. Hold 30s each side.', duration: '2 min' },
      ],
      rest: 'No heavy deadlifts or barbell squats for 48–72h. Keep moving with easy walking.',
      strengthen: [
        { name: 'Romanian Deadlift', how: 'Hinge at hips, flat back, feel hamstring load. 3x10.', duration: '6 min' },
        { name: 'Bird Dog', how: 'Extend opposite arm and leg, hold 3s. 3x10 each side.', duration: '5 min' },
        { name: 'Back Extensions (45°)', how: 'Hinge at hips over pad, squeeze glutes at top. 3x12.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Muscle strain', 'Disc herniation', 'Poor hip hinge mechanics', 'Sitting too long'],
      immediate: [
        { name: 'Walking', how: 'Short 10–15 min walks are better than bed rest for most low back pain.' },
        { name: 'Ice then Heat', how: 'Ice first 48h for acute strain, then switch to heat.' },
        { name: 'McKenzie Extension', how: 'Lie on stomach, prop on forearms (sphinx). 5x30s. Often reduces disc pain.' },
      ],
      stretch: [
        { name: 'Child\'s Pose', how: 'Hold 60–90s. Decompresses lumbar spine.' },
        { name: 'Hip Flexor Lunge', how: 'Tight hip flexors anteriorly tilt pelvis, stressing low back. Stretch them.' },
        { name: 'Piriformis Stretch', how: 'Figure-4 stretch on back. 45s each side.' },
      ],
      strengthen: [
        { name: 'Glute Bridges', how: 'Feet flat, drive hips up squeezing glutes. Key for back pain relief. 3x20.', duration: '5 min' },
        { name: 'Dead Bug', how: 'Core stability reduces low back loading. 3x8 each side.', duration: '5 min' },
        { name: 'McGill Big 3', how: 'Modified curl-up + bird dog + side plank. Evidence-based back rehab protocol.', duration: '10 min' },
      ],
      see_doctor: 'If pain radiates past knee, you have bladder/bowel changes, or woke up with sudden severe pain.',
    },
  },

  glutes: {
    id: 'glutes',
    name: 'Glutes',
    view: 'back',
    color: '#a8c5da',
    description: 'Gluteus maximus, medius, minimus — hip extension, abduction, and stabilization.',
    worked: {
      stretch: [
        { name: 'Pigeon Pose', how: 'Front shin on ground, lean forward over it. 60s each side.', duration: '4 min' },
        { name: 'Figure-4 Stretch', how: 'On back, cross ankle over knee, pull both legs toward chest. 45s each.', duration: '3 min' },
        { name: 'Seated Piriformis', how: 'Cross leg, lean forward over it. 30s each side.', duration: '2 min' },
      ],
      rest: 'Avoid heavy squats/deadlifts for 48h. Hip circles and walking are fine.',
      strengthen: [
        { name: 'Barbell Hip Thrust', how: 'Bar on hips, drive up squeezing glutes hard at top. 3x10.', duration: '8 min' },
        { name: 'Single-Leg Glute Bridge', how: 'One foot on ground, extend other leg, drive up. 3x12.', duration: '6 min' },
        { name: 'Lateral Band Walks', how: 'Band above knees, squat slightly, step sideways 15 steps each. 3 sets.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Piriformis syndrome', 'Glute tendinopathy', 'DOMS from squats/deadlifts', 'Sciatica'],
      immediate: [
        { name: 'Figure-4 Stretch', how: 'If it\'s piriformis — this is the primary release.' },
        { name: 'Ice', how: 'Ice over the painful area 15 min.' },
      ],
      stretch: [
        { name: 'Pigeon Pose', how: '60–90s. Best deep glute and external rotator stretch.' },
        { name: 'Supine Figure-4', how: 'Thread needle for piriformis. 45s each side.' },
      ],
      strengthen: [
        { name: 'Clamshells', how: 'Band above knees, side-lying, open and close like clamshell. 3x20.', duration: '5 min' },
        { name: 'Single-Leg Hip Thrust', how: 'Progressive load on glute. Start with bodyweight. 3x12.', duration: '6 min' },
      ],
      see_doctor: 'If pain shoots down the back of the leg (possible sciatica), or sits right at the sitting bone.',
    },
  },

  hamstrings: {
    id: 'hamstrings',
    name: 'Hamstrings',
    view: 'back',
    color: '#a8c5da',
    description: 'Biceps femoris, semitendinosus, semimembranosus — flex the knee and extend the hip.',
    worked: {
      stretch: [
        { name: 'Standing Hamstring Stretch', how: 'Foot on elevated surface, lean forward with flat back. 45s each.', duration: '2 min' },
        { name: 'Supine Hamstring Stretch', how: 'Lying on back, loop towel around foot, pull gently. 30s.', duration: '2 min' },
        { name: 'Seated Forward Fold', how: 'Legs straight, hinge forward from hips (not rounding back). 30–45s.', duration: '2 min' },
      ],
      rest: 'Avoid sprinting and stiff-leg deadlifts for 48h. Low-intensity cycling OK.',
      strengthen: [
        { name: 'Nordic Curls', how: 'Kneel, have feet held, lower body forward under control. 3x5.', duration: '6 min' },
        { name: 'Romanian Deadlift', how: 'Bar close to body, hinge at hips, feel hamstring load. 3x10.', duration: '7 min' },
        { name: 'Lying Leg Curl', how: 'Machine or slider. Full range of motion. 3x10–12.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Strain from sprinting or kicking', 'Proximal hamstring tendinopathy', 'Sitting-related pain at sit bone', 'DOMS'],
      immediate: [
        { name: 'Ice', how: '15–20 min at site of pain (back of thigh).' },
        { name: 'Avoid Full Stretch', how: 'Counterintuitively, avoid aggressive stretching with acute strain — it worsens it.' },
      ],
      stretch: [
        { name: 'Supine Hamstring Stretch', how: 'Gentle — only go to where you feel tightness, not pain.' },
        { name: 'Standing Desk Stretch', how: 'Foot on low surface, small forward lean. For day-to-day relief.' },
      ],
      strengthen: [
        { name: 'Eccentric Nordic Curls', how: 'Lower only, help yourself up. Best hamstring injury prevention exercise. 3x5.', duration: '6 min' },
        { name: 'Single-Leg RDL', how: 'Balance on one leg, hinge to load hamstring eccentrically. 3x10.', duration: '6 min' },
      ],
      see_doctor: 'If you felt a pop in the back of the thigh, or if sit-bone pain doesn\'t improve in 3–4 weeks.',
    },
  },

  calves: {
    id: 'calves',
    name: 'Calves (Gastrocnemius & Soleus)',
    view: 'back',
    color: '#a8c5da',
    description: 'Plantar-flex the ankle — critical for walking, running, and jumping.',
    worked: {
      stretch: [
        { name: 'Wall Calf Stretch', how: 'Straight leg for gastrocnemius, bent knee for soleus. 45s each.', duration: '3 min' },
        { name: 'Downward Dog', how: 'Push heels toward floor, alternate bending each knee. 60s.', duration: '2 min' },
        { name: 'Step Stretch', how: 'Heel off step, lower gently. Hold 30s.', duration: '1 min' },
      ],
      rest: 'Avoid running and jumping for 24h. Easy walking and swimming are fine.',
      strengthen: [
        { name: 'Standing Calf Raises', how: 'Full range of motion on a step. 3x20–25.', duration: '5 min' },
        { name: 'Seated Calf Raises', how: 'Targets soleus more. Heavier weight, 3x15.', duration: '5 min' },
        { name: 'Single-Leg Calf Raises', how: 'Progress to single leg for Achilles health. 3x15 each.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Calf strain', 'Achilles tendinopathy', 'DOMS from running', 'Deep vein thrombosis (DVT - serious)'],
      immediate: [
        { name: 'RICE', how: 'Rest, Ice (15 min), Compression (light sleeve), Elevation.' },
        { name: 'Gentle Walking', how: 'For mild DOMS, easy walking helps. Stop if pain worsens.' },
      ],
      stretch: [
        { name: 'Seated Towel Stretch', how: 'Loop towel around foot, gently pull toes toward shin. 30s.' },
        { name: 'Wall Stretch', how: 'Both straight and bent-knee versions. 45s each, each side.' },
      ],
      strengthen: [
        { name: 'Eccentric Calf Raises', how: 'Rise on two legs, lower on one. 3x15. Standard Achilles rehab protocol.', duration: '5 min' },
        { name: 'Isometric Calf Hold', how: 'Stand on tiptoe, hold 45s. 3 sets. Low-load Achilles option.', duration: '4 min' },
      ],
      see_doctor: 'If calf is swollen, warm, and painful to touch (possible DVT), or if Achilles feels thick/nodular.',
    },
  },
  adductors: {
    id: 'adductors',
    name: 'Adductors (Inner Thigh)',
    view: 'front',
    color: '#a8c5da',
    description: 'Groin muscles that pull the legs together and stabilize the hip.',
    worked: {
      stretch: [
        { name: 'Butterfly Stretch', how: 'Sit, feet together, knees out, press gently with elbows. Hold 45s.', duration: '2 min' },
        { name: 'Side Lunge Stretch', how: 'Step wide to one side, bend that knee, keep other leg straight. 30s each.', duration: '2 min' },
        { name: 'Standing Groin Stretch', how: 'Feet wide, turn one foot out, lean toward that side. 30s each.', duration: '2 min' },
      ],
      rest: 'Avoid wide-stance squats and lateral movements for 24–48h.',
      strengthen: [
        { name: 'Copenhagen Plank', how: 'Side plank with top foot on a bench, lift bottom leg. 3x20–30s each.', duration: '5 min' },
        { name: 'Cable Hip Adduction', how: 'Ankle attachment, pull leg across body. 3x15 each.', duration: '5 min' },
        { name: 'Sumo Squat', how: 'Wide stance, toes out. 3x12. Great adductor loader.', duration: '6 min' },
      ],
    },
    hurts: {
      likely_causes: ['Groin strain from sprinting/kicking', 'Adductor tendinopathy', 'Sports hernia', 'Hip impingement'],
      immediate: [
        { name: 'Rest & Ice', how: 'Avoid lateral movements. Ice the inner thigh for 15 min.' },
        { name: 'Gentle Walking', how: 'Straight-line walking is usually fine. Avoid side steps.' },
      ],
      stretch: [
        { name: 'Butterfly Stretch', how: 'Gentle — no bouncing. Only go to where you feel a pull, not pain.' },
        { name: 'Supine Hip Rotation', how: 'Lie on back, let knee fall out to side gently. 30s.' },
      ],
      strengthen: [
        { name: 'Isometric Adductor Squeeze', how: 'Ball or pillow between knees, squeeze 10s. 3x10. Safe early-stage rehab.', duration: '4 min' },
        { name: 'Single-Leg Balance', how: 'Standing on one leg, maintain balance. Activates hip stabilizers. 3x30s.', duration: '4 min' },
      ],
      see_doctor: 'If pain is in the pubic bone, or groin pain doesn\'t improve after 2–3 weeks of rest.',
    },
  },

  serratus: {
    id: 'serratus',
    name: 'Serratus Anterior',
    view: 'front',
    color: '#a8c5da',
    description: 'The "boxer\'s muscle" — protracts the scapula and essential for shoulder health.',
    worked: {
      stretch: [
        { name: 'Doorway Lat/Side Stretch', how: 'Hold door frame, rotate body away to stretch the ribcage side. 30s each.', duration: '2 min' },
        { name: 'Side Bend', how: 'Reach arm overhead and lean away. Feel the stretch along your ribs. 30s each.', duration: '1 min' },
      ],
      rest: 'Avoid overhead pressing for 24h. Easy pulling movements are fine.',
      strengthen: [
        { name: 'Serratus Wall Slides', how: 'Forearms on wall, slide arms up while pushing into wall. Feel ribs flare out. 3x10.', duration: '5 min' },
        { name: 'Push-Up Plus', how: 'At the top of a push-up, push the floor away and round upper back extra. 3x12.', duration: '5 min' },
        { name: 'Cable Punch', how: 'Press cable straight forward and "punch" through at end. 3x15.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Winging scapula', 'Overhead overuse', 'Long thoracic nerve irritation', 'Post-viral serratus palsy (rare)'],
      immediate: [
        { name: 'Posture Check', how: 'Avoid rounding forward. Keep shoulder blade flat against ribs.' },
        { name: 'Avoid Overhead', how: 'No overhead pressing or pull-downs until pain-free.' },
      ],
      stretch: [
        { name: 'Pec Minor Stretch', how: 'Tight pec minor inhibits serratus — doorway stretch at 90°. 30s.' },
        { name: 'Thoracic Foam Roll', how: 'Roll mid-back to open the chest and ribcage. 2 min.' },
      ],
      strengthen: [
        { name: 'Wall Slide with Serratus Focus', how: 'Very slowly slide arms up wall, maintain scapula contact. 3x8.', duration: '5 min' },
        { name: 'Dead Bug with Press', how: 'Hold weight overhead in dead bug, focus on scapular connection. 3x8.', duration: '5 min' },
      ],
      see_doctor: 'If your shoulder blade visibly "wings" outward when pressing a wall, or if there\'s numbness along the ribs.',
    },
  },

  rotator_cuff: {
    id: 'rotator_cuff',
    name: 'Rotator Cuff',
    view: 'back',
    color: '#a8c5da',
    description: 'SITS muscles (supraspinatus, infraspinatus, teres minor, subscapularis) — shoulder stabilizers.',
    worked: {
      stretch: [
        { name: 'Sleeper Stretch', how: 'Lie on sore shoulder, push forearm toward the floor gently. 30s each side.', duration: '2 min' },
        { name: 'Cross-Body Stretch', how: 'Pull arm across chest. Feel in the back/outer shoulder. 30s.', duration: '1 min' },
      ],
      rest: 'No overhead pressing or throwing for 48h. Band external rotations are OK light.',
      strengthen: [
        { name: 'External Rotation (Band)', how: 'Elbow at 90°, rotate forearm outward. 3x15 each. Key rotator cuff builder.', duration: '5 min' },
        { name: 'Side-Lying ER', how: 'Lying on side, raise forearm with light dumbbell. 3x12.', duration: '5 min' },
        { name: 'Face Pulls', how: 'Rope to face, elbows high and out. Excellent for cuff health. 3x20.', duration: '5 min' },
      ],
    },
    hurts: {
      likely_causes: ['Rotator cuff tear or strain', 'Subacromial impingement', 'Bicep tendon irritation', 'Overuse from throwing/swimming'],
      immediate: [
        { name: 'Ice', how: '15–20 min on the shoulder. Especially after activity.' },
        { name: 'Avoid Aggravating Positions', how: 'No arm behind back, no overhead reach, no sleeping on it.' },
      ],
      stretch: [
        { name: 'Pendulum Exercise', how: 'Lean over, let arm hang, make small gentle circles. Decompress the joint.' },
        { name: 'Sleeper Stretch', how: 'Gentle — the single best stretch for posterior capsule tightness.' },
      ],
      strengthen: [
        { name: 'ER with Band', how: 'Start very light. This is often painful early — stay below pain threshold.', duration: '5 min' },
        { name: 'Prone Y Raises', how: 'Lying on bench, raise arms in Y shape, thumbs up. 3x12.', duration: '4 min' },
      ],
      see_doctor: 'If you can\'t lift arm to 90°, felt a pop, or have pain at night — may need MRI to rule out full tear.',
    },
  },
};

export const muscleGroups = Object.values(muscles);
