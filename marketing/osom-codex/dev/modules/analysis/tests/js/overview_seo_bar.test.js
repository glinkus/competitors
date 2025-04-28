import '../../js/overview_seo_bar';

describe('overview_seo_bar.js', () => {
  beforeEach(() => {
    // reset DOM and global score
    document.body.innerHTML = '';
    window.seoScore = undefined;
  });

  it('does nothing when seoScoreOverviewBar is not in the DOM', () => {
    window.seoScore = 85;
    expect(() => {
      document.dispatchEvent(new Event('DOMContentLoaded'));
    }).not.toThrow();
  });

  it('applies bg-success when score >= 70', () => {
    window.seoScore = 75;
    const bar = document.createElement('div');
    bar.id = 'seoScoreOverviewBar';
    document.body.appendChild(bar);

    document.dispatchEvent(new Event('DOMContentLoaded'));

    expect(bar.style.width).toBe('75%');
    expect(bar.textContent).toBe('75%');
    expect(bar.classList.contains('bg-success')).toBe(true);
    expect(bar.classList.contains('bg-warning')).toBe(false);
    expect(bar.classList.contains('bg-danger')).toBe(false);
  });

  it('applies bg-warning when score >= 40 and < 70', () => {
    window.seoScore = 55;
    const bar = document.createElement('div');
    bar.id = 'seoScoreOverviewBar';
    document.body.appendChild(bar);

    document.dispatchEvent(new Event('DOMContentLoaded'));

    expect(bar.style.width).toBe('55%');
    expect(bar.textContent).toBe('55%');
    expect(bar.classList.contains('bg-success')).toBe(false);
    expect(bar.classList.contains('bg-warning')).toBe(true);
    expect(bar.classList.contains('bg-danger')).toBe(false);
  });

  it('applies bg-danger when score < 40', () => {
    window.seoScore = 30;
    const bar = document.createElement('div');
    bar.id = 'seoScoreOverviewBar';
    document.body.appendChild(bar);

    document.dispatchEvent(new Event('DOMContentLoaded'));

    expect(bar.style.width).toBe('30%');
    expect(bar.textContent).toBe('30%');
    expect(bar.classList.contains('bg-success')).toBe(false);
    expect(bar.classList.contains('bg-warning')).toBe(false);
    expect(bar.classList.contains('bg-danger')).toBe(true);
  });
});
