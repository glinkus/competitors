import KeywordAnalysis from '../../js/keyword_analysis';

describe('KeywordAnalysis', () => {
    beforeEach(() => {
        // Correctly stub getContext
        HTMLCanvasElement.prototype.getContext = jest.fn(function () {
          return { canvas: this }; // the canvas element itself
        });
      
        // Mock global Chart constructor
        global.Chart = jest.fn().mockImplementation(() => ({
          destroy: jest.fn(),
          update: jest.fn()
        }));
      
        // Mock Bootstrap Modal
        global.bootstrap = {
          Modal: jest.fn().mockImplementation(el => ({
            show: jest.fn()
          }))
        };
      
        // Set up DOM
        document.body.innerHTML = `
          <div id="keywordTrendModal" class="modal">
            <h5 id="keywordTrendModalLabel"></h5>
            <canvas id="trendChartModal"></canvas>
            <canvas id="regionChartModal"></canvas>
          </div>
        `;
      });
      

  it('has openKeywordModal method', () => {
    const ka = new KeywordAnalysis([]);
    expect(typeof ka.openKeywordModal).toBe('function');
  });

  it('renders two charts and shows the modal when opened', () => {
    const sample = {
      keyword: 'foo',
      trend_keys: JSON.stringify(['Jan', 'Feb']),
      trend_values: JSON.stringify([10, 20]),
      interest_by_region: { US: 5, CA: 15 }
    };
    const ka = new KeywordAnalysis([sample]);
    ka.openKeywordModal(0);

    // simulate modal shown event
    const modalEl = document.getElementById('keywordTrendModal');
    modalEl.dispatchEvent(new Event('shown.bs.modal'));

    // Chart should be called twice (line + pie)
    expect(Chart).toHaveBeenCalledTimes(2);

    // first call for trend chart uses correct context
    const [trendCtxArg] = Chart.mock.calls[0];
    expect(trendCtxArg.canvas.id).toBe('trendChartModal');

    // second call for region chart uses correct context
    const [regionCtxArg] = Chart.mock.calls[1];
    expect(regionCtxArg.canvas.id).toBe('regionChartModal');

  });
});
