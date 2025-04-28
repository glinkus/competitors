import '../../js/overview_modal_cleanup';

describe('overview_modal_cleanup.js', () => {
  beforeEach(() => {
    // reset DOM and body state before each test
    document.body.innerHTML = '';
    document.body.className = '';
    document.body.style.cssText = '';
  });

  it('does nothing when keywordTrendModal does not exist', () => {
    // should not throw even if modal isn't on the page
    expect(() => {
      document.dispatchEvent(new Event('DOMContentLoaded'));
    }).not.toThrow();
  });

  it('removes modal-open class, clears style, and removes backdrop when present', () => {
    // setup modal and backdrop
    const modal = document.createElement('div');
    modal.id = 'keywordTrendModal';
    document.body.appendChild(modal);
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    document.body.appendChild(backdrop);

    // simulate an open modal state
    document.body.classList.add('modal-open');
    document.body.style.backgroundColor = 'red';

    // register the listener
    document.dispatchEvent(new Event('DOMContentLoaded'));
    // trigger the cleanup
    modal.dispatchEvent(new Event('hidden.bs.modal'));

    expect(document.body.classList.contains('modal-open')).toBe(false);
    expect(document.body.style.backgroundColor).toBe('');
    expect(document.querySelector('.modal-backdrop')).toBeNull();
  });

  it('removes modal-open class and clears style even when no backdrop', () => {
    // setup only the modal
    const modal = document.createElement('div');
    modal.id = 'keywordTrendModal';
    document.body.appendChild(modal);

    // simulate an open modal state
    document.body.classList.add('modal-open');
    document.body.style.margin = '10px';

    // register and trigger
    document.dispatchEvent(new Event('DOMContentLoaded'));
    modal.dispatchEvent(new Event('hidden.bs.modal'));

    expect(document.body.classList.contains('modal-open')).toBe(false);
    expect(document.body.style.margin).toBe('');
  });
});
