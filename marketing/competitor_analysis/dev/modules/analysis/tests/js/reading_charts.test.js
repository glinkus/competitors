import ReadingCharts from '../../js/reading_charts';

describe('ReadingCharts', () => {
  it('can be constructed', () => {
    const rc = new ReadingCharts();
    expect(typeof rc.init).toBe('function');
  });

  it('logs initialized message', () => {
    console.info = jest.fn();
    new ReadingCharts();
    expect(console.info).toHaveBeenCalledWith('[ReadingCharts] initialized.');
  });

  describe('init', () => {
    beforeEach(() => {
      document.body.innerHTML = '';
      delete window.Chart;
      delete window.readingLabels;
      delete window.readingValues;
      delete window.readabilityValues;
    });

    it('creates both charts if both canvases present', () => {
      const timeCanvas = document.createElement('canvas');
      timeCanvas.id = 'readingTimeChart';
      document.body.appendChild(timeCanvas);
      const readabilityCanvas = document.createElement('canvas');
      readabilityCanvas.id = 'readabilityChart';
      document.body.appendChild(readabilityCanvas);

      window.readingLabels = ['a', 'b'];
      window.readingValues = [1, 2];
      window.readabilityValues = [90, 95];

      const mockChart = jest.fn();
      window.Chart = mockChart;

      const rc = new ReadingCharts();
      rc.init();
      document.dispatchEvent(new Event('DOMContentLoaded'));

      expect(mockChart).toHaveBeenCalledTimes(2);
      expect(mockChart).toHaveBeenCalledWith(
        timeCanvas,
        expect.objectContaining({
          type: 'line',
          data: expect.objectContaining({ labels: ['a', 'b'] })
        })
      );
      expect(mockChart).toHaveBeenCalledWith(
        readabilityCanvas,
        expect.objectContaining({
          type: 'line',
          data: expect.objectContaining({
            datasets: expect.arrayContaining([
              expect.objectContaining({ label: 'Readability Score' })
            ])
          })
        })
      );
    });

    it('creates time chart when only time canvas present', () => {
      const timeCanvas = document.createElement('canvas');
      timeCanvas.id = 'readingTimeChart';
      document.body.appendChild(timeCanvas);

      window.readingLabels = [];
      window.readingValues = [];
      window.readabilityValues = [];

      const mockChart = jest.fn();
      window.Chart = mockChart;

      const rc = new ReadingCharts();
      rc.init();
      document.dispatchEvent(new Event('DOMContentLoaded'));

      expect(mockChart).toHaveBeenCalledTimes(2);
      expect(mockChart).toHaveBeenCalledWith(timeCanvas, expect.any(Object));
    });

    it('creates readability chart when only readability canvas present', () => {
      const readabilityCanvas = document.createElement('canvas');
      readabilityCanvas.id = 'readabilityChart';
      document.body.appendChild(readabilityCanvas);

      window.readingLabels = ['x'];
      window.readingValues = [3];
      window.readabilityValues = [75];

      const mockChart = jest.fn();
      window.Chart = mockChart;

      const rc = new ReadingCharts();
      rc.init();
      document.dispatchEvent(new Event('DOMContentLoaded'));

      expect(mockChart).toHaveBeenCalledTimes(3);
      expect(mockChart).toHaveBeenCalledWith(readabilityCanvas, expect.any(Object));
    });

    it('does nothing if no canvases', () => {
      window.Chart = jest.fn();
      const rc = new ReadingCharts();
      rc.init();
      document.dispatchEvent(new Event('DOMContentLoaded'));
      expect(window.Chart).not.toHaveBeenCalled();
    });
  });
});
