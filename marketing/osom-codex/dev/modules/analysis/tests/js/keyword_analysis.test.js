import KeywordAnalysis from '../../js/keyword_analysis';

describe('KeywordAnalysis', () => {
  it('has openKeywordModal method', () => {
    const ka = new KeywordAnalysis([]);
    expect(typeof ka.openKeywordModal).toBe('function');
  });
});
