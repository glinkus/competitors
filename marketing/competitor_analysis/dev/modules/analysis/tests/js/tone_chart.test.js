import ToneChart from '../../js/tone_chart';

describe('ToneChart', () => {
  it('stores provided chartId', () => {
    const tc = new ToneChart('myChart');
    expect(tc.chartId).toBe('myChart');
  });

  it('logs initialized message', () => {
    console.info = jest.fn();
    new ToneChart('any');
    expect(console.info).toHaveBeenCalledWith('[ToneChart] initialized.');
  });

  describe('init', () => {
    beforeEach(() => {
      document.body.innerHTML = '';
      delete window.Chart;
      delete window.tpyeLabels;
      delete window.toneData;
    });

    //integration test
    it('creates chart when element present', () => {
      const canvas = document.createElement('canvas');
      canvas.id = 'chartId';
      const fakeCtx = {};
      canvas.getContext = jest.fn().mockReturnValue(fakeCtx);
      document.body.appendChild(canvas);

      window.tpyeLabels = ['x','y'];
      window.toneData = [10,20];

      const mockChart = jest.fn();
      window.Chart = mockChart;

      const tc = new ToneChart('chartId');
      tc.init();
      document.dispatchEvent(new Event('DOMContentLoaded'));

      expect(mockChart).toHaveBeenCalledTimes(1);
      expect(mockChart).toHaveBeenCalledWith(
        fakeCtx,
        expect.objectContaining({
          type: 'bar',
          data: {
            labels: ['x','y'],
            datasets: expect.arrayContaining([
              expect.objectContaining({
                label: 'Tone Score (%)',
                data: [10,20]
              })
            ])
          },
          options: expect.objectContaining({
            indexAxis: 'y'
          })
        })
      );
    });

    it('does nothing if no element found', () => {
      window.Chart = jest.fn();
      const tc = new ToneChart('missingId');
      tc.init();
      document.dispatchEvent(new Event('DOMContentLoaded'));
      expect(window.Chart).not.toHaveBeenCalled();
    });
  });
});
