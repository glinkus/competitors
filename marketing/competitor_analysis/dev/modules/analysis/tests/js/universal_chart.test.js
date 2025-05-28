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

  describe('init', () => {
    beforeEach(() => {
      document.body.innerHTML = '';
      window.Chart = jest.fn();
    });

    it('attaches click listener to trigger', () => {
      document.body.innerHTML = `
        <button id="t1"></button>
        <canvas id="c1"></canvas>
        <select id="m1"><option value="a">a</option></select>
      `;
      const cfg = {
        chartId: 'c1',
        triggerId: 't1',
        metricSelectId: 'm1',
        chartTypeSelectId: 'ct1',
        labels: [],
        datasets: { a: [1] }
      };
      const chart = new UniversalMetricChart(cfg);
      chart.render = jest.fn();
      chart.init();
      document.getElementById('t1').click();
      expect(chart.render).toHaveBeenCalled();
    });
  });

  describe('render', () => {
    let cfg, canvas, mockChart;
    beforeEach(() => {
      document.body.innerHTML = `
        <canvas id="c1"></canvas>
        <select id="m1"><option value="a">a</option></select>
        <select id="ct1"><option value="bar">bar</option></select>
      `;
      canvas = document.getElementById('c1');
      mockChart = jest.fn().mockReturnValue({ destroy: jest.fn() });
      window.Chart = mockChart;
      cfg = {
        chartId: 'c1',
        triggerId: 't1',
        metricSelectId: 'm1',
        chartTypeSelectId: 'ct1',
        labels: ['L1'],
        datasets: { a: [5], b: [6] }
      };
    });

    //integration test
    it('renders chart for object‐based datasets', () => {
      const chart = new UniversalMetricChart(cfg);
      chart.render();
      expect(mockChart).toHaveBeenCalledWith(
        canvas,
        expect.objectContaining({ type: 'bar' })
      );
      expect(mockChart).toHaveBeenCalledWith(
        canvas,
        expect.objectContaining({
          data: expect.objectContaining({
            datasets: expect.arrayContaining([
              expect.objectContaining({ data: [5] })
            ])
          })
        })
      );
    });

    //integration test
    it('renders chart for array‐of‐objects datasets', () => {
      cfg.datasets = [{ key: 'x', values: [10] }, { key: 'y', values: [20] }];
      document.getElementById('m1').innerHTML =
        '<option value="x">x</option><option value="y">y</option>';
      document.getElementById('m1').value = 'y';
      const chart = new UniversalMetricChart(cfg);
      chart.render();
      expect(mockChart).toHaveBeenCalledWith(
        canvas,
        expect.objectContaining({
          data: expect.objectContaining({
            datasets: expect.arrayContaining([
              expect.objectContaining({ data: [20] })
            ])
          })
        })
      );
    });

    //integration test
    it('renders chart for simple array datasets', () => {
      cfg.datasets = [1, 2, 3];
      const chart = new UniversalMetricChart(cfg);
      chart.render();
      expect(mockChart).toHaveBeenCalledWith(
        canvas,
        expect.objectContaining({
          data: expect.objectContaining({
            datasets: expect.arrayContaining([
              expect.objectContaining({ data: [1, 2, 3] })
            ])
          })
        })
      );
    });

    it('destroys existing chart before re‐render', () => {
      const chart = new UniversalMetricChart(cfg);
      chart.render();
      chart.render();
      expect(mockChart().destroy).toHaveBeenCalled();
    });
  });
});
