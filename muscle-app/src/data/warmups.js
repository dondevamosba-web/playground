export const warmups = {
  neck: [
    { name: 'Neck Self-Massage', type: 'foam_roll', duration: '30s each side', cue: 'Use fingertips to find tight spots along the base of the skull and upper traps — hold on tender points.' },
    { name: 'Chin Tucks', type: 'mobility', reps: '10', cue: 'Glide your chin straight back, creating a double chin — hold 2s each rep to reset forward head posture.' },
    { name: 'Lateral Neck Stretch', type: 'dynamic', reps: '8 each side', cue: 'Ear to shoulder with slow control — let gravity do the work, no pulling with your hand.' },
    { name: 'Neck Rotation', type: 'dynamic', reps: '10 each direction', cue: 'Rotate through full range at a steady pace, pausing briefly at end range on each side.' },
    { name: 'Scapular Retraction', type: 'activation', reps: '15', cue: 'Pinch shoulder blades together for 2s each rep — this stabilizes the neck-shoulder chain before loading.' },
  ],

  traps_front: [
    { name: 'Upper Trap Foam Roll', type: 'foam_roll', duration: '40s each side', cue: 'Place the roller between the neck and shoulder and let your arm hang — find the dense band and breathe into it.' },
    { name: 'Chest-Opener Stretch', type: 'mobility', duration: '30s each side', cue: 'Doorframe stretch at 90° — step through and feel the front of the shoulder and chest open.' },
    { name: 'Shoulder Circles', type: 'dynamic', reps: '15 each direction', cue: 'Full range, slow and deliberate — let your arms trace large circles without shrugging.' },
    { name: 'Band Pull-Apart', type: 'activation', reps: '20', cue: 'Keep arms straight and pull the band to chest level — squeeze rear delts at full extension.' },
    { name: '50% Lateral Raise', type: 'ramp', reps: '15', cue: 'Light weight, move slowly, just pump blood into the shoulder girdle.' },
  ],

  chest: [
    { name: 'Pec Minor Foam Roll', type: 'foam_roll', duration: '45s each side', cue: 'Position roller just inside the shoulder on the pec — find the tight spot and hold 20s while breathing.' },
    { name: 'Arm Circles', type: 'dynamic', reps: '20 each direction', cue: 'Start small and gradually increase range until you feel full shoulder mobility.' },
    { name: 'Band Pull-Apart', type: 'activation', reps: '20', cue: 'Keep arms straight and squeeze shoulder blades at the end of each rep to counterbalance the pressing pattern.' },
    { name: '50% Push-Up Set', type: 'ramp', reps: '10', cue: 'Easy, controlled reps — just pushing blood into the chest and shoulders.' },
    { name: '60% Bench Press', type: 'ramp', reps: '8', cue: 'Groove the movement pattern and feel the chest loading — not a work set.' },
  ],

  shoulders: [
    { name: 'Thoracic Spine Foam Roll', type: 'foam_roll', duration: '60s', cue: 'Roll slowly from mid to upper back, pausing at stiff segments — open your arms wide to expose the spine.' },
    { name: 'Wall Slides', type: 'mobility', reps: '10', cue: 'Keep elbows and wrists glued to the wall as you slide overhead — feel the thoracic extension and shoulder mobility.' },
    { name: 'Band External Rotation', type: 'activation', reps: '15 each arm', cue: 'Elbow at 90°, rotate out against the band — this primes the rotator cuff before pressing.' },
    { name: 'Cuban Press', type: 'activation', reps: '10 light', cue: 'Row to 90°, externally rotate, then press — a full rotator cuff and deltoid primer in one movement.' },
    { name: '50% Overhead Press', type: 'ramp', reps: '10', cue: 'Light load, full range — establish the movement pattern and confirm shoulder mobility is ready.' },
  ],

  biceps: [
    { name: 'Forearm Foam Roll', type: 'foam_roll', duration: '30s each arm', cue: 'Roll from elbow to wrist on the underside of the forearm — the biceps tendon feeds into the forearm fascia.' },
    { name: 'Wrist Flexor Stretch', type: 'mobility', duration: '30s each side', cue: 'Arm straight, palm up, gently pull fingers back with your other hand — hold the stretch without bouncing.' },
    { name: 'Shoulder Dislocates', type: 'dynamic', reps: '10', cue: 'Use a wide grip on a band or stick and rotate overhead and behind — this opens the bicep and shoulder simultaneously.' },
    { name: 'Supination Drill', type: 'activation', reps: '15 each arm', cue: 'Hold a light dumbbell vertically and rotate forearm fully pronated to supinated — wakes up the supinator and biceps.' },
    { name: '40% Barbell Curl', type: 'ramp', reps: '12', cue: 'Light and slow — full range of motion to pump blood into the elbow joint and bicep belly.' },
  ],

  forearms: [
    { name: 'Forearm Roller or Lacrosse Ball', type: 'foam_roll', duration: '40s each side', cue: 'Press and roll along the flexor and extensor compartments of the forearm — pause on dense spots.' },
    { name: 'Wrist Circles', type: 'dynamic', reps: '15 each direction', cue: 'Full range rotation, slow and controlled — both clockwise and counterclockwise.' },
    { name: 'Finger Extensions Against Band', type: 'activation', reps: '20', cue: 'Wrap a light band around fingers and extend against resistance — balances the flexor dominance from gripping.' },
    { name: 'Wrist Flexion/Extension with Light DB', type: 'activation', reps: '15 each', cue: 'Slow, full range curls and reverse curls — no swinging, just controlled wrist movement.' },
    { name: 'Dead Hang', type: 'mobility', duration: '20–30s', cue: 'Passive hang from a bar — decompresses the wrist and elbow while loading grip tissue lightly.' },
  ],

  abs: [
    { name: 'Thoracic Rotation', type: 'dynamic', reps: '10 each side', cue: 'Seated or in quadruped — rotate through the upper back while keeping hips stable.' },
    { name: 'Cat-Cow', type: 'mobility', reps: '10 breath cycles', cue: 'Move through full spinal flexion and extension, coordinating breath with movement.' },
    { name: 'Dead Bug', type: 'activation', reps: '8 each side', cue: 'Press lower back flat and move opposite arm and leg — establishes deep core co-contraction before loading.' },
    { name: 'Hollow Body Hold', type: 'activation', duration: '3 x 15s', cue: 'Flatten your lower back, arms overhead, legs low — feel the full anterior core engage.' },
    { name: '50% Cable Crunch', type: 'ramp', reps: '12', cue: 'Light weight, full spinal flexion — feel the abs working through the whole range before adding load.' },
  ],

  obliques: [
    { name: 'Side-Lying Foam Roll (Lat/QL)', type: 'foam_roll', duration: '40s each side', cue: 'Roll from the hip to the armpit along the side body — pausing where you feel tension in the lateral chain.' },
    { name: 'Standing Side Bend', type: 'dynamic', reps: '10 each side', cue: 'Reach overhead and bend laterally, letting your rib cage move away from your hip — no rotation.' },
    { name: 'World\'s Greatest Stretch', type: 'mobility', reps: '5 each side', cue: 'Lunge with rotation — reach your inside hand to the floor and rotate your outside arm skyward.' },
    { name: 'Pallof Press', type: 'activation', reps: '10 each side', cue: 'Press straight out and resist rotation — this teaches the obliques to brace anti-rotationally.' },
    { name: 'Light Russian Twist', type: 'ramp', reps: '20', cue: 'Bodyweight or minimal load — deliberate rotation, pausing at each end to feel the oblique engage.' },
  ],

  hip_flexors: [
    { name: 'Hip Flexor Foam Roll', type: 'foam_roll', duration: '45s each side', cue: 'Lie face down with the roller on the front of the hip, just below the ASIS — breathe and let it release.' },
    { name: 'Kneeling Hip Flexor Stretch', type: 'mobility', duration: '45s each side', cue: 'Posterior pelvic tilt (tuck your tailbone) while in a kneeling lunge — this isolates the stretch to the hip flexor.' },
    { name: 'Leg Swings', type: 'dynamic', reps: '15 each direction each leg', cue: 'Forward/back and cross-body swings — hold a wall for balance and let momentum carry you through full range.' },
    { name: 'Hip 90/90 Drill', type: 'mobility', duration: '30s each side', cue: 'Sit with both legs bent at 90° — lean into each position and breathe to progressively deepen the hip rotation.' },
    { name: 'Reverse Lunge with Reach', type: 'activation', reps: '8 each side', cue: 'Step back and reach the opposite arm overhead — this stretches and activates the hip flexor in the same movement.' },
  ],

  quads: [
    { name: 'Quad Foam Roll', type: 'foam_roll', duration: '60s each side', cue: 'Roll from hip to just above knee on the front of the thigh — pause and flex/extend at tight spots.' },
    { name: 'Kneeling Quad Stretch', type: 'mobility', duration: '40s each side', cue: 'From a kneeling lunge, reach back and hold your rear foot — pull heel toward your glute and tuck your pelvis.' },
    { name: 'Leg Swings', type: 'dynamic', reps: '15 each leg', cue: 'Forward and backward pendulum swings — allow the knee to bend on the back swing to stretch the quad.' },
    { name: 'Air Squat', type: 'activation', reps: '15 slow', cue: 'Deep, controlled squats with a 3-second descent — build proprioceptive awareness before loading.' },
    { name: '50% Squat', type: 'ramp', reps: '10', cue: 'Feel the pattern, not the load — establish depth, bracing, and knee tracking before adding weight.' },
  ],

  calves_front: [
    { name: 'Shin Foam Roll', type: 'foam_roll', duration: '30s each side', cue: 'Kneel and roll the front of the shin from below the knee to the ankle — often overlooked and surprisingly tight.' },
    { name: 'Ankle Circles', type: 'dynamic', reps: '15 each direction', cue: 'Full range rotation to mobilize the ankle joint — both clockwise and counterclockwise per ankle.' },
    { name: 'Toe Taps', type: 'activation', reps: '25', cue: 'Standing, rapidly tap toes up and down — this wakes up the tibialis anterior and dorsiflexors.' },
    { name: 'Ankle Dorsiflexion Wall Drill', type: 'mobility', reps: '10 each side', cue: 'Stand close to a wall and drive your knee forward over your toe — increases ankle mobility for squatting.' },
    { name: 'Heel Walk', type: 'activation', duration: '20 meters', cue: 'Walk on your heels with toes raised — activates the shins and reinforces dorsiflexion strength.' },
  ],

  adductors: [
    { name: 'Adductor Foam Roll', type: 'foam_roll', duration: '45s each side', cue: 'Lie face down, roll the inner thigh from groin to just above the knee — roll slowly and pause on tight spots.' },
    { name: 'Lateral Lunge Stretch', type: 'mobility', reps: '8 each side', cue: 'Step wide, shift weight over one leg, and sit into the hip — keep the opposite leg straight to stretch the adductor.' },
    { name: '90/90 Hip Switch', type: 'dynamic', reps: '10', cue: 'Rotate between both 90/90 positions smoothly — opens hip internal and external rotation which feeds adductor mobility.' },
    { name: 'Sumo Squat Hold', type: 'mobility', duration: '45s', cue: 'Wide stance deep squat, elbows on inner knees — breathe and let the adductors gradually release.' },
    { name: 'Copenhagen Plank (Short Lever)', type: 'activation', duration: '3 x 10s each side', cue: 'Knee on bench, not ankle — shorter lever, still loads the adductors effectively as a primer.' },
  ],

  serratus: [
    { name: 'Thoracic Foam Roll', type: 'foam_roll', duration: '60s', cue: 'Roll mid-spine, arms crossed or overhead — pausing at stiff segments to restore thoracic extension.' },
    { name: 'Cat-Cow Protraction', type: 'dynamic', reps: '10', cue: 'At the top of each cat, actively push the floor away and round your upper back maximally to engage the serratus.' },
    { name: 'Serratus Wall Slide', type: 'activation', reps: '12', cue: 'Forearms on wall, actively protract your shoulder blades as you slide up — the serratus should feel the effort.' },
    { name: 'Push-Up Plus', type: 'activation', reps: '12', cue: 'At the top of a push-up, add a final push — round the upper back by protracting scapulae against the load.' },
    { name: '50% Cable Fly or Push-Up', type: 'ramp', reps: '10', cue: 'Light, full range — feel the serratus at end range of protraction as you close the movement.' },
  ],

  upper_back: [
    { name: 'Thoracic Foam Roll', type: 'foam_roll', duration: '90s', cue: 'Arms crossed over chest, roll from T4 to T12 — pause at restricted segments and breathe into the extension.' },
    { name: 'Thread the Needle', type: 'mobility', reps: '8 each side', cue: 'From quadruped, slide one arm under your body — rotate through the thoracic spine, not the lumbar.' },
    { name: 'Band Pull-Apart', type: 'activation', reps: '20', cue: 'Arms straight, pull the band to chest height and squeeze shoulder blades hard at the end position.' },
    { name: 'Face Pull', type: 'activation', reps: '15 light', cue: 'Pull to the face with high elbows and externally rotate at the end — primes the mid-back and rotator cuff together.' },
    { name: '50% Cable Row', type: 'ramp', reps: '12', cue: 'Light, slow, focus on scapular retraction and depression — feel the upper back working before adding load.' },
  ],

  lats: [
    { name: 'Lat Foam Roll', type: 'foam_roll', duration: '45s each side', cue: 'Lie on your side, roller in the armpit along the lat — roll slowly and hold where it\'s dense.' },
    { name: 'Overhead Lat Stretch', type: 'mobility', duration: '30s each side', cue: 'Hold a rack, step back, and push your hips away — feel the lat stretch from hip to armpit.' },
    { name: 'Dead Hang', type: 'mobility', duration: '30s', cue: 'Passive hang from a bar — decompress the shoulder and lengthen the lat before pulling movements.' },
    { name: 'Straight-Arm Pulldown', type: 'activation', reps: '15 light', cue: 'Arms straight, pull the cable to your hips — isolates the lat without involving the biceps.' },
    { name: '50% Lat Pulldown', type: 'ramp', reps: '12', cue: 'Full range with deliberate scapular depression at the top — feel the lats engaged before adding load.' },
  ],

  triceps: [
    { name: 'Triceps Lacrosse Ball', type: 'foam_roll', duration: '30s each arm', cue: 'Pin the ball between your tricep and the floor or a wall — roll the muscle belly from elbow to just below the shoulder.' },
    { name: 'Overhead Triceps Stretch', type: 'mobility', duration: '30s each side', cue: 'Elbow to ceiling, hand behind your head — use your other hand to gently push the elbow further back.' },
    { name: 'Elbow Circles', type: 'dynamic', reps: '15 each direction', cue: 'Small, controlled circles at the elbow joint — warms the joint capsule before extension-heavy work.' },
    { name: 'Resistance Band Pushdown', type: 'activation', reps: '20', cue: 'Light band, full extension on every rep — squeeze the triceps hard at lockout to prime the muscle.' },
    { name: '50% Close-Grip Press or Pushdown', type: 'ramp', reps: '10', cue: 'Feel the tricep working through a full range — just getting blood in before the working sets.' },
  ],

  lower_back: [
    { name: 'QL Foam Roll', type: 'foam_roll', duration: '45s each side', cue: 'Sit on the roller at the side of your lower back, just above the hip — lean into the QL and breathe deeply.' },
    { name: 'Knee-to-Chest Stretch', type: 'mobility', duration: '30s each side', cue: 'Lie on your back and hug one knee in — feel the lumbar spine decompress and the QL lengthen.' },
    { name: 'Cat-Cow', type: 'dynamic', reps: '12 breath cycles', cue: 'Slow and deliberate spinal movement — coordinate full flexion with exhale and full extension with inhale.' },
    { name: 'Bird Dog', type: 'activation', reps: '8 each side', cue: 'Extend opposite arm and leg while keeping the lumbar spine neutral — trains the erectors and multifidus.' },
    { name: '50% Good Morning or RDL', type: 'ramp', reps: '10', cue: 'Light load, feel the hinge pattern — confirm the lower back is stable and the hamstrings are loose before adding weight.' },
  ],

  glutes: [
    { name: 'Glute Foam Roll', type: 'foam_roll', duration: '45s each side', cue: 'Sit on the roller, cross one ankle over the opposite knee — roll into the piriformis and glute medius.' },
    { name: 'Pigeon Stretch', type: 'mobility', duration: '45s each side', cue: 'Front shin parallel (as able), lean your torso forward — breathe into the external hip rotators and glute.' },
    { name: 'Leg Swings (Lateral)', type: 'dynamic', reps: '15 each leg', cue: 'Cross-body swings — hold a wall and swing each leg across your body and out wide to mobilize the hip.' },
    { name: 'Banded Clamshell', type: 'activation', reps: '20 each side', cue: 'Keep your pelvis still and rotate your top knee skyward — this fires the glute medius before compound lifts.' },
    { name: '50% Hip Thrust', type: 'ramp', reps: '12', cue: 'Establish the pelvic tuck and glute squeeze at the top before adding weight.' },
  ],

  hamstrings: [
    { name: 'Hamstring Foam Roll', type: 'foam_roll', duration: '45s each side', cue: 'Roll from just below the glute to just above the knee — cross one leg over the other for more pressure.' },
    { name: 'Standing Hamstring Stretch', type: 'mobility', duration: '30s each side', cue: 'Hinge forward with a flat back, one foot elevated — feel the stretch in the belly of the hamstring.' },
    { name: 'Leg Swings (Forward/Back)', type: 'dynamic', reps: '15 each leg', cue: 'Forward swing reaches forward leg straight, back swing keeps knee slightly bent — full hip hinge range.' },
    { name: 'Nordic Curl Eccentric (Slow)', type: 'activation', reps: '5 each side', cue: 'Resist the fall over 5 seconds — this eccentric load warms the hamstring tissue and builds tension tolerance.' },
    { name: '50% RDL', type: 'ramp', reps: '10', cue: 'Light bar or dumbbells, feel the hinge and hamstring loading — confirm mobility is ready before heavier sets.' },
  ],

  calves: [
    { name: 'Calf Foam Roll', type: 'foam_roll', duration: '45s each side', cue: 'Roll from ankle to just below the knee — cross one ankle over the other for added pressure on dense spots.' },
    { name: 'Ankle Dorsiflexion Stretch', type: 'mobility', duration: '30s each side', cue: 'Stand on a step, let the heel drop below the edge — slow, sustained calf stretch through full range.' },
    { name: 'Ankle Circles', type: 'dynamic', reps: '15 each direction', cue: 'Full range rotation — warms the ankle joint before any push-off dominant movement.' },
    { name: 'Double-Leg Calf Raise Hold', type: 'activation', duration: '3 x 10s', cue: 'Rise onto toes and hold — isometric loading warms the Achilles and calf at end range before dynamic work.' },
    { name: 'Bodyweight Calf Raise', type: 'ramp', reps: '20', cue: 'Full range, slow eccentric — feel the entire calf working before loading with weight.' },
  ],

  rotator_cuff: [
    { name: 'Pec Minor Foam Roll', type: 'foam_roll', duration: '40s each side', cue: 'Roll just inside the shoulder on the pec — tight pec minor is one of the main contributors to rotator cuff overload.' },
    { name: 'Sleeper Stretch', type: 'mobility', duration: '30s each side', cue: 'Lie on your side, stack shoulders, and gently press your forearm toward the floor — stretches the posterior capsule.' },
    { name: 'External Rotation with Band', type: 'activation', reps: '15 each side', cue: 'Elbow fixed at 90°, rotate outward against the band — prime infraspinatus and teres minor before pressing.' },
    { name: 'Internal Rotation with Band', type: 'activation', reps: '15 each side', cue: 'Mirror of external rotation — complete the pair to balance subscapularis and the cuff as a unit.' },
    { name: 'Cuban Press (Light DB)', type: 'ramp', reps: '10', cue: 'Row to 90°, externally rotate to 90°, then press — this sequence loaded lightly is a full rotator cuff ramp-up.' },
  ],
};
