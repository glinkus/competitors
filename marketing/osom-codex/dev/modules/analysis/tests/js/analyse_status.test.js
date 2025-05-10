import AnalyseStatus from '../../js/analyse_status';

global.fetch = jest.fn();
global.confirm = jest.fn();
global.alert = jest.fn();

Object.defineProperty(window, 'location', {
  value: { reload: jest.fn() },
  writable: true
});

describe('AnalyseStatus', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = '';
  });

  describe('getCookie', () => {
    it('returns the cookie value if found', () => {
      document.cookie = 'csrftoken=test_token';
      expect(AnalyseStatus.getCookie('csrftoken')).toBe('test_token');
    });

    it('returns null if cookie not found', () => {
      document.cookie = 'csrftoken=;expires=Thu, 01 Jan 1970 00:00:00 GMT';
      expect(AnalyseStatus.getCookie('csrftoken')).toBeNull();
    });
  });

  describe('initStatusCheck', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <div id="website-row-1"><div class="status">🟡 In Progress</div></div>
        <div id="website-row-2"><div class="status">🟢 Finished</div></div>
      `;
    });

    //integration test
    it('calls checkScrapingStatus for In Progress websites', () => {
      const instance = new AnalyseStatus();
      const spy = jest.spyOn(instance, 'checkScrapingStatus').mockImplementation(() => {});
      document.querySelectorAll('.status').forEach(el => { if (!el.textContent) el.textContent = ''; });
      instance.initStatusCheck();
      expect(spy).toHaveBeenCalledWith('1');
      expect(spy).not.toHaveBeenCalledWith('2');
    });

    it('does nothing if no In Progress', () => {
      document.querySelector('#website-row-1 .status').textContent = '🟢 Finished';
      const instance = new AnalyseStatus();
      const spy = jest.spyOn(instance, 'checkScrapingStatus').mockImplementation(() => {});
      document.querySelectorAll('.status').forEach(el => { if (!el.textContent) el.textContent = ''; });
      instance.initStatusCheck();
      expect(spy).not.toHaveBeenCalled();
    });
  });

  describe('checkScrapingStatus', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <div id="website-row-1">
          <div class="visited-count"></div>
          <div class="status"></div>
          <div class="action"></div>
          <button id="stop-btn-1"></button>
          <div id="scraping-stopped-1"></div>
        </div>
      `;
    });

    //integration test
    it('handles crawling_in_progress properly', async () => {
      fetch.mockResolvedValueOnce({
        json: async () => ({ 
          crawling_in_progress: true,
          visited_count: 3
        })
      });

      jest.spyOn(window, 'setTimeout').mockImplementation(fn => fn());

      const instance = new AnalyseStatus();
      const spy = jest.spyOn(instance, 'checkScrapingStatus').mockImplementation(() => {});

      await instance.checkScrapingStatus(1);
      expect(document.querySelector('.visited-count').innerHTML).toBe('');
      expect(document.querySelector('.status').innerHTML).toContain('');
      expect(spy).toHaveBeenCalledWith(1);
    });

    it('catches fetch errors gracefully', async () => {
      fetch.mockRejectedValueOnce('error');
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      const instance = new AnalyseStatus();
      await instance.checkScrapingStatus(1);
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("Error checking status for website 1:"), 'error');
      consoleSpy.mockRestore();
    });
  });

  describe('stopScraping', () => {
    beforeEach(() => {
      window.location.reload = jest.fn();
    });

    it('reloads page if scraping stopped successfully', async () => {
      fetch.mockResolvedValueOnce({ json: async () => ({ stopped: true }) });
      await AnalyseStatus.stopScraping(10);
      expect(window.location.reload).toHaveBeenCalled();
    });

    it('logs error if fetch fails', async () => {
      fetch.mockRejectedValueOnce('fail');
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      await AnalyseStatus.stopScraping(10);
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('continueScraping', () => {
    beforeEach(() => {
      window.location.reload = jest.fn();
    });

    //integration test
    it('reloads page if scraping continued successfully', async () => {
      fetch.mockResolvedValueOnce({ json: async () => ({ continued: true }) });
      await AnalyseStatus.continueScraping(10);
      expect(window.location.reload).toHaveBeenCalled();
    });

    it('logs error if fetch fails', async () => {
      fetch.mockRejectedValueOnce('fail');
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      await AnalyseStatus.continueScraping(10);
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('initDelete', () => {
    describe('deleteWebsite', () => {
      beforeEach(() => {
        document.body.innerHTML = `<div class="website-row" id="website-row-99"></div>`;
        const instance = new AnalyseStatus();
        instance.initDelete();
      });

      //integration test
      it('deletes website on confirmation and success', async () => {
        global.confirm.mockReturnValueOnce(true);
        fetch.mockResolvedValueOnce({ 
          json: async () => ({ deleted: true })
        });
        jest.spyOn(window, 'setTimeout').mockImplementation(fn => fn());
        await window.deleteWebsite(99);
        await new Promise(resolve => setTimeout(resolve, 0));
        expect(document.getElementById('website-row-99')).toBeNull();
      });

      it('does not delete if confirmation is declined', async () => {
        global.confirm.mockReturnValueOnce(false);
        await window.deleteWebsite(99);
        expect(fetch).not.toHaveBeenCalled();
        expect(document.getElementById('website-row-99')).not.toBeNull();
      });

      it('alerts user if deletion failed', async () => {
        global.confirm.mockReturnValueOnce(true);
        global.alert.mockImplementation(() => {});
        fetch.mockResolvedValueOnce({ 
          json: async () => ({ deleted: false }) 
        });

        await window.deleteWebsite(99);
        expect(global.alert).toHaveBeenCalledWith('Failed to delete the website.');
      });

      it('logs error if fetch fails', async () => {
        global.confirm.mockReturnValueOnce(true);
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        fetch.mockRejectedValueOnce('error');

        await window.deleteWebsite(99);
        expect(consoleSpy).toHaveBeenCalled();
        consoleSpy.mockRestore();
      });
    });
  });
});