import UniversalMetricChart from '../../js/universal_chart';

describe('UniversalMetricChart', () => {
  it('maps config into instance properties', () => {
    const cfg = {
      chartId: 'c1',
      triggerId: 't1',
      metricSelectId: 'm1',
      chartTypeSelectId: 'ct1',
      labels: ['a','b'],
      datasets: { a: [1], b: [2] }
    };
    const chart = new UniversalMetricChart(cfg);
    expect(chart.chartId).toBe('c1');
    expect(chart.triggerId).toBe('t1');
    expect(chart.metricSelectId).toBe('m1');
    expect(chart.chartTypeSelectId).toBe('ct1');
    expect(chart.labels).toEqual(['a','b']);
    expect(chart.datasets).toEqual({ a: [1], b: [2] });
  });
});
