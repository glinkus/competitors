jest.useFakeTimers();

describe('overview_audience.js', () => {
  beforeEach(() => {
    jest.resetModules();
    // prepare DOM
    document.body.innerHTML = `
      <ul id="target-audience-list" class="d-none"></ul>
      <div id="target-audience-loading"></div>
    `;
    // ensure URL
    window.audienceStatusUrl = 'http://test/audience';
    // mock fetch
    global.fetch = jest.fn();
  });

  it('fetches and renders audience when ready', async () => {
    // stub ready response
    fetch.mockResolvedValue({
      json: () => Promise.resolve({
        ready: true,
        audience: { Seg1: 'Exp1', Seg2: 'Exp2' }
      })
    });

    require('../../js/overview_audience');
    document.dispatchEvent(new Event('DOMContentLoaded'));

    // allow promises to resolve
    await Promise.resolve();
    await Promise.resolve();

    const listEl = document.getElementById('target-audience-list');
    const loadingEl = document.getElementById('target-audience-loading');

    expect(fetch).toHaveBeenCalledWith('http://test/audience');
    expect(loadingEl.classList.contains('d-none')).toBe(true);
    expect(listEl.classList.contains('d-none')).toBe(false);
    expect(listEl.children).toHaveLength(2);
    expect(listEl.textContent).toContain('Seg1:');
    expect(listEl.textContent).toContain('Exp1');
  });

  it('retries fetch when not ready', async () => {
    // stub not-ready response
    fetch.mockResolvedValue({
      json: () => Promise.resolve({ ready: false })
    });

    require('../../js/overview_audience');
    document.dispatchEvent(new Event('DOMContentLoaded'));

    // initial fetch
    await Promise.resolve();
    expect(fetch).toHaveBeenCalledTimes(1);

    // advance timer for retry
    jest.advanceTimersByTime(3000);
    await Promise.resolve();
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
