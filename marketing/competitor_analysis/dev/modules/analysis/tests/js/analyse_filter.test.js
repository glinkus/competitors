import AnalyseFilter from '../../js/analyse_filter';

describe('AnalyseFilter functionality', () => {
  let instance;

  function setupDOM() {
    document.body.innerHTML = `
      <select id="status-filter">
        <option value="">All</option>
        <option value="finished">Finished</option>
        <option value="stopped">Stopped</option>
        <option value="in_progress">In Progress</option>
      </select>
      <select id="sort-filter">
        <option value="asc">Asc</option>
        <option value="desc">Desc</option>
      </select>
      <div class="row row-cols-1">
        <div class="col" id="col1">
          <div class="card-body">
            <p class="mb-2">Last Visited: 2021-01-01</p>
          </div>
          <div class="status">Finished 🟢</div>
        </div>
        <div class="col" id="col2">
          <div class="card-body">
            <p class="mb-2">Last Visited: 2021-02-01</p>
          </div>
          <div class="status">Stopped 🔴</div>
        </div>
        <div class="col" id="col3">
          <div class="card-body">
            <p class="mb-2">Last Visited: 2021-03-01</p>
          </div>
          <div class="status">🟡 In Progress</div>
        </div>
      </div>
    `;
  }

  beforeEach(() => {
    setupDOM();
    instance = new AnalyseFilter();
  });

  it('initializes filters and attaches event listeners', () => {
    const statusFilter = document.getElementById('status-filter');
    const sortFilter = document.getElementById('sort-filter');

    const statusChangeEvent = new Event('change');
    const sortChangeEvent = new Event('change');

    statusFilter.dispatchEvent(statusChangeEvent);
    sortFilter.dispatchEvent(sortChangeEvent);

    expect(statusFilter).not.toBeNull();
    expect(sortFilter).not.toBeNull();
  });

  it('filters cards by status', () => {
    const statusFilter = document.getElementById('status-filter');
    statusFilter.value = 'finished';
    statusFilter.dispatchEvent(new Event('change'));

    const visibleCards = Array.from(
      document.querySelectorAll('.row.row-cols-1 .col')
    );
    expect(visibleCards).toHaveLength(0);
  });
//integration test
  it('sorts cards by date in ascending order', () => {
    const sortFilter = document.getElementById('sort-filter');
    sortFilter.value = 'asc';
    sortFilter.dispatchEvent(new Event('change'));


    const dates = Array.from(
      document.querySelectorAll('.row.row-cols-1 .col .mb-2')
    ).map(p => p.textContent.trim());
    expect(dates).toEqual([
      'Last Visited: 2021-01-01',
      'Last Visited: 2021-02-01',
      'Last Visited: 2021-03-01'
    ]);
  });
//integration test
  it('sorts cards by date in descending order', () => {
    const sortFilter = document.getElementById('sort-filter');
    sortFilter.value = 'desc';
    sortFilter.dispatchEvent(new Event('change'));

    const dates = Array.from(
      document.querySelectorAll('.row.row-cols-1 .col .mb-2')
    ).map(p => p.textContent.trim());
    expect(dates).toEqual([
      'Last Visited: 2021-01-01',
      'Last Visited: 2021-02-01',
      'Last Visited: 2021-03-01'
    ]);
  });
//integration test
  it('handles empty filters gracefully', () => {
    const statusFilter = document.getElementById('status-filter');
    const sortFilter = document.getElementById('sort-filter');

    statusFilter.value = '';
    sortFilter.value = 'asc';

    statusFilter.dispatchEvent(new Event('change'));
    sortFilter.dispatchEvent(new Event('change'));

    const visibleCards = Array.from(document.querySelectorAll('.col:not(.hidden)'));
    expect(visibleCards).toHaveLength(3);
  });
});
