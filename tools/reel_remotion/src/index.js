const { registerRoot, Composition } = require("remotion");
const { OlaReel, SLIDES_DATA, SLIDE_FRAMES } = require("./OlaReel");

const TOTAL_FRAMES = SLIDES_DATA.length * SLIDE_FRAMES;

registerRoot(() => {
  return (
    <Composition
      id="OlaDigitalReel"
      component={OlaReel}
      durationInFrames={TOTAL_FRAMES}
      fps={30}
      width={1080}
      height={1920}
    />
  );
});
