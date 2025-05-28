import AnalyseCompare from '../../js/analyse_compare';

describe('AnalyseCompare', () => {
  it('defines initCompare', () => {
    const ac = new AnalyseCompare();
    expect(typeof ac.initCompare).toBe('function');
  });
});

function setupDOM() {
  document.body.innerHTML = `
    <button id="start-compare-btn">Select websites to compare</button>
    <button id="compare-btn" hidden disabled>Compare</button>
    <input id="compare-ids" value="" />
    <div class="card" data-id="1">
      <div class="compare-check d-none"><input type="checkbox" value="1"></div>
      <div class="status">Finished 🟢</div>
    </div>
    <div class="card" data-id="2">
      <div class="compare-check d-none"><input type="checkbox" value="2"></div>
      <div class="status">Finished 🟢</div>
    </div>
    <div class="card" data-id="3">
      <div class="compare-check d-none"><input type="checkbox" value="3"></div>
      <div class="status">Failed 🔴</div>
    </div>
  `;
}

describe('AnalyseCompare functionality', () => {
  let ac;
  beforeEach(() => {
    document.body.innerHTML = '';
    setupDOM();
    ac = new AnalyseCompare();
    ac.initCompare();
  });

  it('toggles compare mode and shows/hides checkboxes', () => {
    const startBtn = document.getElementById('start-compare-btn');
    const wrappers = document.querySelectorAll('.compare-check');
    expect(startBtn.textContent).toBe('Select websites to compare');
    startBtn.click();
    expect(startBtn.textContent).toBe('Cancel Compare');
    wrappers.forEach(w => expect(w.classList.contains('d-none')).toBe(false));
    startBtn.click();
    expect(startBtn.textContent).toBe('Select websites to compare');
    wrappers.forEach(w => expect(w.classList.contains('d-none')).toBe(true));
  });

  it('enables compare button only when two checkboxes are checked', () => {
    const startBtn = document.getElementById('start-compare-btn');
    const compareBtn = document.getElementById('compare-btn');
    const compareIds = document.getElementById('compare-ids');
    startBtn.click();
    const inputs = Array.from(document.querySelectorAll('.compare-check input'));
    inputs[0].click();
    expect(compareBtn.disabled).toBe(true);
    inputs[1].click();
    expect(compareBtn.disabled).toBe(false);
    expect(compareIds.value).toBe('1,2');
  });

  it('blocks a third selection and shows an alert', () => {
    jest.spyOn(window, 'alert').mockImplementation(() => {});
    const startBtn = document.getElementById('start-compare-btn');
    startBtn.click();
    const inputs = Array.from(document.querySelectorAll('.compare-check input'));
    inputs[0].click();
    inputs[1].click();
    inputs[2].click();
    expect(window.alert).toHaveBeenCalledWith('You can compare a maximum of 2 websites.');
    expect(inputs[2].checked).toBe(false);
  });
});
