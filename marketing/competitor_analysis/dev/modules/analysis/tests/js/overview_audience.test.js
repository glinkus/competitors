jest.useFakeTimers();

describe('overview_audience.js', () => {
  beforeEach(() => {
    jest.resetModules();
    document.body.innerHTML = `
      <ul id="target-audience-list" class="d-none"></ul>
      <div id="target-audience-loading"></div>
    `;
    window.audienceStatusUrl = 'http://test/audience';
    global.fetch = jest.fn();
  });
  
  it('fetches and renders audience when ready', async () => {
    fetch.mockResolvedValue({
      json: () => Promise.resolve({
        ready: true,
        audience: { Seg1: 'Exp1', Seg2: 'Exp2' }
      })
    });

    require('../../js/overview_audience');
    document.dispatchEvent(new Event('DOMContentLoaded'));

    await Promise.resolve();
    await Promise.resolve();

    const listEl = document.getElementById('target-audience-list');
    const loadingEl = document.getElementById('target-audience-loading');

    expect(fetch).toHaveBeenCalledWith('http://test/audience');
    expect(loadingEl.classList.contains('d-none')).toBe(false);
    expect(listEl.classList.contains('d-none')).toBe(true);
    expect(listEl.children).toHaveLength(0);
  });

  it('retries fetch when not ready', async () => {
    fetch.mockResolvedValue({
      json: () => Promise.resolve({ ready: false })
    });

    require('../../js/overview_audience');
    document.dispatchEvent(new Event('DOMContentLoaded'));

    await Promise.resolve();
    expect(fetch).toHaveBeenCalledTimes(2);

    jest.advanceTimersByTime(3000);
    await Promise.resolve();
    await Promise.resolve();
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
