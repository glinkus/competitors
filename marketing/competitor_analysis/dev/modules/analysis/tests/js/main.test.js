import Analysis from '../../js/main';

describe('Analysis', () => {
  it('is a constructor', () => {
    expect(typeof Analysis).toBe('function');
    const a = new Analysis();
    expect(a).toBeInstanceOf(Analysis);
  });
});
