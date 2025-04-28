import ToneChart from '../../js/tone_chart';

describe('ToneChart', () => {
  it('stores provided chartId', () => {
    const tc = new ToneChart('myChart');
    expect(tc.chartId).toBe('myChart');
  });
});
