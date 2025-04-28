import '../../js/overview_technology';

describe('overview_technology.js', () => {
  beforeEach(() => {
    // reset DOM
    document.body.innerHTML = `
      <div id="technology-loading"></div>
      <ul id="technology-list"></ul>
      <ul id="backend-stack-list"></ul>
    `;
    window.technologyStatusUrl = '/test-url';
    jest.useRealTimers();
    jest.clearAllMocks();
    window.fetch = jest.fn();
  });

  it('defines globals and doesn’t throw on import', () => {
    expect(typeof window.technologyStatusUrl).toBe('string');
    expect(typeof fetch).toBe('function');
  });

  it('renders lists and summary when ready=true with summary', async () => {
    window.fetch.mockResolvedValueOnce({
      json: () => Promise.resolve({
        ready: true,
        technology: { React: 'lib', Vue: 'framework' },
        backend_stack: { Node: 'runtime' },
        technology_summary: 'All good'
      })
    });

    document.dispatchEvent(new Event('DOMContentLoaded'));
    // flush pending promise callbacks
    await new Promise(resolve => setTimeout(resolve, 0));

    const listEl = document.getElementById('technology-list');
    // two tech <li> plus one <p.summary>
    expect(listEl.children.length).toBe(3);
    expect(listEl.textContent).toContain('React:');
    const summaryEl = listEl.querySelector('p.summary');
    expect(summaryEl).not.toBeNull();
    expect(summaryEl.textContent).toBe('All good');
  });

  it('renders fallback summary when technology_summary missing', async () => {
    window.fetch.mockResolvedValueOnce({
      json: () => Promise.resolve({
        ready: true,
        technology: { JS: 'lang' },
        backend_stack: {}
      })
    });

    document.dispatchEvent(new Event('DOMContentLoaded'));
    await new Promise(resolve => setTimeout(resolve, 0));

    const listEl = document.getElementById('technology-list');
    expect(listEl.children.length).toBe(2); // one tech <li> + fallback <p.summary>
    const summaryEl = listEl.querySelector('p.summary');
    expect(summaryEl).not.toBeNull();
    expect(summaryEl.textContent).toBe('No technology stack detected.');
  });

  it('retries when ready=false', async () => {
    jest.useFakeTimers();
    window.fetch.mockResolvedValue({ json: () => Promise.resolve({ ready: false }) });

    document.dispatchEvent(new Event('DOMContentLoaded'));
    // flush initial promise callbacks
    await Promise.resolve();
    await Promise.resolve();
    expect(fetch).toHaveBeenCalledTimes(1);

    jest.advanceTimersByTime(3000);
    // allow the scheduled checkTechnologyReady() to run
    await Promise.resolve();
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('logs error on fetch rejection', async () => {
    const err = new Error('fail');
    window.fetch.mockRejectedValueOnce(err);
    console.error = jest.fn();

    document.dispatchEvent(new Event('DOMContentLoaded'));
    // flush pending promise callbacks
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(console.error).toHaveBeenCalledWith('Error loading technology data:', err);
  });
});
