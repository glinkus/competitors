import ReadingCharts from '../../js/reading_charts';

describe('ReadingCharts', () => {
  it('can be constructed', () => {
    const rc = new ReadingCharts();
    expect(typeof rc.init).toBe('function');
  });
});
