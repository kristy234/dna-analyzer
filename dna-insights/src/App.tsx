import React, { useState, useEffect, useRef, useCallback } from 'react';
import { parseDNAFile } from './utils/parseDNAFile';
import './index.css';
import { unzipSync, strFromU8 } from 'fflate';

type Match = {
  rsid: string;
  gene: string;
  summary: string;
  magnitude: number;
  repute: string;
};

const CARDS_PER_PAGE = 20;

const App: React.FC = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [progress, setProgress] = useState(-1);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [fileLoaded, setFileLoaded] = useState(false);
  const [visibleCount, setVisibleCount] = useState(CARDS_PER_PAGE);
  const observerTarget = useRef<HTMLDivElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setError(null);
      setFileLoaded(true);
      setVisibleCount(CARDS_PER_PAGE);
      setProgress(0);

      console.log('Inflating SNPedia data...');
      const res = await fetch(`${import.meta.env.BASE_URL}genotypes_by_rsid.zip`);
      const zipped = new Uint8Array(await res.arrayBuffer());
      const unzipped = unzipSync(zipped);
      const jsonText = strFromU8(unzipped['genotypes_by_rsid.json']);
      const snpediaData = JSON.parse(jsonText);

      console.log('Uploading file...');
      const matches = await parseDNAFile(file, snpediaData, setProgress);

      // Show loading spinner only during rendering
      console.log('Sorting matches...');
      setIsLoading(true);
      matches.sort((a, b) => b.magnitude - a.magnitude);
      setMatches(matches);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : 'An error occurred while processing the file');
    } finally {
      setIsLoading(false);
      console.log('Done!');
    }
  };

  const loadMore = useCallback(() => {
    if (isLoading) return;

    setIsLoading(true);
    setTimeout(() => {
      setVisibleCount(prev => Math.min(prev + CARDS_PER_PAGE, matches.length));
      setIsLoading(false);
    }, 300);
  }, [isLoading, matches.length]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && visibleCount < matches.length) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => {
      if (observerTarget.current) {
        observer.unobserve(observerTarget.current);
      }
    };
  }, [loadMore, visibleCount, matches.length]);

  const visibleMatches = matches.slice(0, visibleCount);

  return (
    <div className="app-container">
      <div className="content-section">
        <h1>DNA Insights Viewer</h1>
        
        <div className="disclaimer">
          <p><strong>Disclaimer:</strong> This tool is for informational purposes only. Genetic data from SNPedia may be incomplete, outdated, or misinterpreted without context. Do not use it for medical or diagnostic decisions. Always consult a healthcare professional for advice.</p>
        </div>
        
        <div className="attribution">
          <p>Genetic data sourced from <a href="https://www.snpedia.com/" target="_blank" rel="noopener noreferrer">SNPedia</a> under CC-BY-NC-SA 3.0 license.</p>
        </div>
        
        {!fileLoaded && (
          <div className="file-upload-section">
            <input
              type="file"
              accept=".txt"
              onChange={handleFileUpload}
              style={{ marginBottom: '1rem' }}
            />
            <p>Upload your DNA file to see insights about your genetic markers</p>
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {progress >= 0 && progress < 100 && (
          <div className="progress-wrapper">
            <div className="progress-bar" style={{ width: `${progress}%` }} />
            <p className="loading-text">Uploading file: {progress}%</p>
          </div>
        )}

        {isLoading && (
          <div style={{ textAlign: 'center' }}>
            <div className="loading-spinner" />
            <p className="loading-text">Processing your DNA data...</p>
          </div>
        )}

        {matches.length > 0 && (
          <div className="infinite-scroll-container">
            <div className="genotype-grid">
              {visibleMatches.map(({ rsid, gene, summary, magnitude, repute }) => (
                <div
                  key={rsid}
                  className={`genotype-card ${repute === 'Bad' ? 'bad-repute' : repute === 'Good' ? 'good-repute' : ''}`}
                >
                  <h3>
                    <a
                      href={`https://bots.snpedia.com/index.php/${rsid}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {rsid}
                    </a>
                    {gene && ` (${gene})`}
                  </h3>
                  <p>{summary}</p>
                  <p><em>Repute: {repute}, Magnitude: {magnitude}</em></p>
                </div>
              ))}
            </div>

            {visibleCount < matches.length && (
              <div ref={observerTarget} style={{ height: '20px' }}>
                {isLoading && <div className="load-more-spinner" />}
              </div>
            )}

            {visibleCount >= matches.length && matches.length > 0 && (
              <div className="alert alert-info" style={{ textAlign: 'center', marginTop: '1rem' }}>
                Showing all {matches.length.toLocaleString()} matches
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
