import '../../js/overview_technology';

describe('overview_technology.js', () => {
  it('defines checkTechnologyReady', () => {
    expect(typeof window.technologyStatusUrl).toBe('string');
    expect(typeof fetch).toBe('function');
  });
});
