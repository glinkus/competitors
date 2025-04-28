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

    // Wait for DOM updates after fetch
    await Promise.resolve();
    await Promise.resolve();

    const listEl = document.getElementById('target-audience-list');
    const loadingEl = document.getElementById('target-audience-loading');

    expect(fetch).toHaveBeenCalledWith('http://test/audience');
    expect(loadingEl.classList.contains('d-none')).toBe(false); // Ensure loading is hidden
    expect(listEl.classList.contains('d-none')).toBe(true);  // Ensure list is visible
    expect(listEl.children).toHaveLength(0);
  });

  it('retries fetch when not ready', async () => {
    // stub not-ready response
    fetch.mockResolvedValue({
      json: () => Promise.resolve({ ready: false })
    });

    require('../../js/overview_audience');
    document.dispatchEvent(new Event('DOMContentLoaded'));

    // Wait for the first fetch to resolve
    await Promise.resolve();
    expect(fetch).toHaveBeenCalledTimes(2);

    // Advance timer for retry and wait for the second fetch
    jest.advanceTimersByTime(3000);
    await Promise.resolve();
    await Promise.resolve(); // Ensure all promises resolve
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
