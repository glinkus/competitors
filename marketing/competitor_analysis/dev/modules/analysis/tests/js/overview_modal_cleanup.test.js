import '../../js/overview_modal_cleanup';

describe('overview_modal_cleanup.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    document.body.className = '';
    document.body.style.cssText = '';
  });

  it('does nothing when keywordTrendModal does not exist', () => {
    expect(() => {
      document.dispatchEvent(new Event('DOMContentLoaded'));
    }).not.toThrow();
  });
//integrations tests below
  it('removes modal-open class, clears style, and removes backdrop when present', () => {
    const modal = document.createElement('div');
    modal.id = 'keywordTrendModal';
    document.body.appendChild(modal);
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    document.body.appendChild(backdrop);

    document.body.classList.add('modal-open');
    document.body.style.backgroundColor = 'red';

    document.dispatchEvent(new Event('DOMContentLoaded'));
    modal.dispatchEvent(new Event('hidden.bs.modal'));

    expect(document.body.classList.contains('modal-open')).toBe(false);
    expect(document.body.style.backgroundColor).toBe('');
    expect(document.querySelector('.modal-backdrop')).toBeNull();
  });

  it('removes modal-open class and clears style even when no backdrop', () => {
    const modal = document.createElement('div');
    modal.id = 'keywordTrendModal';
    document.body.appendChild(modal);

    document.body.classList.add('modal-open');
    document.body.style.margin = '10px';

    document.dispatchEvent(new Event('DOMContentLoaded'));
    modal.dispatchEvent(new Event('hidden.bs.modal'));

    expect(document.body.classList.contains('modal-open')).toBe(false);
    expect(document.body.style.margin).toBe('');
  });
});
