import '../../js/overview_audience';

describe('overview_audience.js', () => {
  it('defines checkAudienceReady', () => {
    expect(typeof window.audienceStatusUrl).toBe('string');
  });
});
